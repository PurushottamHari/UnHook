import asyncio
import json
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from redis.asyncio import Redis

# Load environment variables
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    print("❌ REDIS_URL not found in environment variables.")
    exit(1)

# Strip external quotes if they exist in the env value
if REDIS_URL.startswith('"') and REDIS_URL.endswith('"'):
    REDIS_URL = REDIS_URL[1:-1]
elif REDIS_URL.startswith("'") and REDIS_URL.endswith("'"):
    REDIS_URL = REDIS_URL[1:-1]

redis_client: Optional[Redis] = None

SERVICES = ["data_collector_service", "data_processing_service", "newspaper_service"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
    print(f"🚀 Connected to Redis at {REDIS_URL}")
    yield
    if redis_client:
        await redis_client.close()
        print("🛑 Closed Redis connection.")


app = FastAPI(title="Unhook DLQ Dashboard", lifespan=lifespan)


async def get_dlq_messages(service: str):
    stream_name = f"{service}:dead_letter_queue"
    try:
        # Read the last 100 messages from the stream
        messages = await redis_client.xrange(stream_name, count=100)
        formatted_messages = []
        for msg_id, data in messages:
            try:
                payload = json.loads(data.get("payload", "{}"))
                formatted_messages.append(
                    {
                        "id": msg_id,
                        "service": service,
                        "reason": data.get("reason", "Unknown error"),
                        "payload": payload,
                        "timestamp": msg_id.split("-")[
                            0
                        ],  # Redis stream IDs are <timestamp>-<sequence>
                    }
                )
            except Exception as e:
                print(f"Error parsing message {msg_id}: {e}")
        return formatted_messages
    except Exception as e:
        print(f"Error fetching from {stream_name}: {e}")
        return []


@app.get("/api/messages")
async def list_messages():
    all_messages = []
    for service in SERVICES:
        messages = await get_dlq_messages(service)
        all_messages.extend(messages)

    # Sort by timestamp descending
    all_messages.sort(key=lambda x: x["timestamp"], reverse=True)
    return all_messages


@app.post("/api/reprocess/{service}/{msg_id}")
async def reprocess_message(service: str, msg_id: str):
    stream_name = f"{service}:dead_letter_queue"

    # 1. Fetch the message
    messages = await redis_client.xrange(stream_name, min=msg_id, max=msg_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Message not found")

    _, data = messages[0]
    try:
        message_json = json.loads(data.get("payload", "{}"))

        # 2. Transform the message (similar to dlq_to_processing.py logic)
        if "context" in message_json:
            message_json["context"]["retry_count"] = 0
            message_json["context"]["attempts"] = []

        target_service = message_json.get("target_service") or service
        new_topic = f"{target_service}:commands"
        message_json["topic"] = new_topic

        # 3. Add to commands stream
        clean_json = json.dumps(message_json, separators=(",", ":"))
        await redis_client.xadd(new_topic, {"payload": clean_json})

        # 4. Remove from DLQ
        await redis_client.xdel(stream_name, msg_id)

        return {"status": "success", "target": new_topic}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reprocess-insufficient-balance")
async def reprocess_insufficient_balance_messages():
    reprocessed_count = 0
    errors = []

    for service in SERVICES:
        stream_name = f"{service}:dead_letter_queue"
        try:
            # Fetch up to 1000 messages from the DLQ stream to scan
            messages = await redis_client.xrange(stream_name, count=1000)
            for msg_id, data in messages:
                reason = data.get("reason", "")
                # Match "Insufficient Balance" or error "402"
                if "Insufficient Balance" in reason or "402" in reason:
                    try:
                        message_json = json.loads(data.get("payload", "{}"))

                        # Transform the message
                        if "context" in message_json:
                            message_json["context"]["retry_count"] = 0
                            message_json["context"]["attempts"] = []

                        target_service = message_json.get("target_service") or service
                        new_topic = f"{target_service}:commands"
                        message_json["topic"] = new_topic

                        # Add to active commands stream
                        clean_json = json.dumps(message_json, separators=(",", ":"))
                        await redis_client.xadd(new_topic, {"payload": clean_json})

                        # Remove from DLQ
                        await redis_client.xdel(stream_name, msg_id)
                        reprocessed_count += 1
                    except Exception as e:
                        errors.append(
                            f"Error reprocessing {msg_id} in {service}: {str(e)}"
                        )
        except Exception as e:
            errors.append(f"Error reading stream {stream_name}: {str(e)}")

    if errors and reprocessed_count == 0:
        raise HTTPException(status_code=500, detail="; ".join(errors))

    return {
        "status": "success",
        "reprocessed_count": reprocessed_count,
        "errors": errors,
    }


@app.delete("/api/messages/{service}/{msg_id}")
async def delete_message(service: str, msg_id: str):
    stream_name = f"{service}:dead_letter_queue"
    try:
        await redis_client.xdel(stream_name, msg_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", response_class=HTMLResponse)
async def dashboard_ui():
    return """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UnHook DLQ Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Outfit', sans-serif; }
        .glass {
            background: rgba(17, 24, 39, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .message-card {
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .message-card:hover {
            background: rgba(31, 41, 55, 0.8);
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        [x-cloak] { display: none !important; }
        pre::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        pre::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }
    </style>
</head>
<body class="bg-[#0b0f1a] text-gray-100 min-h-screen">
    <div x-data="dlqApp()" x-init="fetchMessages()" class="max-w-7xl mx-auto p-6 md:p-12">
        <!-- Header -->
        <header class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-12">
            <div>
                <h1 class="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-indigo-500 bg-clip-text text-transparent">
                    DLQ Processor
                </h1>
                <p class="text-gray-400 mt-2">Manage and reprocess failed messages across UnHook services.</p>
            </div>
            <div class="flex flex-wrap gap-4">
                <!-- Reprocess Insufficient Balance Errors -->
                <button @click="reprocessBalanceErrors()" 
                        :disabled="reprocessingBalance"
                        class="px-5 py-2.5 rounded-xl flex items-center gap-2 bg-gradient-to-r from-amber-500/20 via-orange-500/20 to-red-500/20 hover:from-amber-500/35 hover:via-orange-500/35 hover:to-red-500/35 border border-amber-500/30 hover:border-amber-500/50 text-amber-300 font-medium transition-all shadow-[0_0_15px_rgba(245,158,11,0.05)] hover:shadow-[0_0_25px_rgba(245,158,11,0.2)] active:scale-[0.98] disabled:opacity-50">
                    <i data-lucide="coins" :class="{ 'animate-bounce': reprocessingBalance }" class="w-5 h-5"></i>
                    Reprocess Balance Errors
                </button>

                <button @click="fetchMessages()" 
                        class="glass px-5 py-2.5 rounded-xl flex items-center gap-2 hover:bg-gray-800 transition-colors">
                    <i data-lucide="refresh-cw" :class="{ 'animate-spin': loading }" class="w-4 h-4"></i>
                    Refresh
                </button>
            </div>
        </header>

        <!-- Stats/Filters -->
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-6 mb-8">
            <template x-for="stat in stats" :key="stat.label">
                <div class="glass p-6 rounded-2xl transition-all hover:scale-[1.02]"
                     :class="stat.label === 'Balance Errors' && stat.value > 0 ? 'border-amber-500/30 bg-amber-500/5 shadow-[0_0_15px_rgba(245,158,11,0.05)]' : ''">
                    <p class="text-gray-400 text-sm mb-1" x-text="stat.label"></p>
                    <p class="text-3xl font-bold" 
                       :class="stat.label === 'Balance Errors' && stat.value > 0 ? 'text-amber-400' : 'text-gray-100'"
                       x-text="stat.value"></p>
                </div>
            </template>
        </div>

        <!-- Messages List -->
        <div class="glass rounded-3xl overflow-hidden">
            <div class="p-6 border-b border-white/10 flex justify-between items-center bg-white/5">
                <h2 class="text-xl font-semibold">Failed Messages</h2>
                <div class="text-sm text-gray-400">Showing last 100 messages</div>
            </div>

            <div class="divide-y divide-white/5">
                <template x-if="loading && messages.length === 0">
                    <div class="p-20 text-center text-gray-500">
                        <i data-lucide="loader-2" class="w-8 h-8 animate-spin mx-auto mb-4"></i>
                        Loading messages...
                    </div>
                </template>

                <template x-if="!loading && messages.length === 0">
                    <div class="p-20 text-center text-gray-500">
                        <i data-lucide="check-circle-2" class="w-8 h-8 mx-auto mb-4 text-green-500"></i>
                        DLQ is empty! Everything looks good.
                    </div>
                </template>

                <template x-for="msg in messages" :key="msg.id">
                    <div class="p-6 message-card cursor-pointer" @click="selectedMessage = msg"
                         :class="msg.reason && (msg.reason.includes('Insufficient Balance') || msg.reason.includes('402')) ? 'border-l-4 border-amber-500/40 bg-amber-500/2' : ''">
                        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                            <div class="flex-1">
                                <div class="flex flex-wrap items-center gap-3 mb-2">
                                    <span class="px-2 py-1 rounded text-xs font-bold uppercase tracking-wider bg-indigo-500/20 text-indigo-400"
                                          x-text="msg.service.replace('_service', '')"></span>
                                    <span class="text-gray-500 text-sm" x-text="formatDate(msg.timestamp)"></span>
                                    <template x-if="msg.reason && (msg.reason.includes('Insufficient Balance') || msg.reason.includes('402'))">
                                        <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
                                            <i data-lucide="alert-circle" class="w-3 h-3"></i>
                                            Balance Error
                                        </span>
                                    </template>
                                </div>
                                <h3 class="text-lg font-medium text-gray-200" x-text="msg.payload.action_name || 'Unknown Action'"></h3>
                                <p class="text-red-400 text-sm mt-1 line-clamp-1" x-text="msg.reason"></p>
                            </div>
                            <div class="flex items-center gap-2 self-end md:self-auto">
                                <button @click.stop="copyCommand(msg)" 
                                        class="p-2 rounded-lg hover:bg-white/10 text-gray-400 transition-colors"
                                        title="Copy Redis Command">
                                    <i data-lucide="copy" class="w-5 h-5"></i>
                                </button>
                                <button @click.stop="deleteMessage(msg)" 
                                        class="p-2 rounded-lg hover:bg-red-500/20 text-red-400 transition-colors"
                                        title="Delete Message">
                                    <i data-lucide="trash-2" class="w-5 h-5"></i>
                                </button>
                                <button @click.stop="reprocess(msg)" 
                                        class="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-colors text-sm font-medium">
                                    Reprocess
                                </button>
                            </div>
                        </div>
                    </div>
                </template>
            </div>
        </div>

        <!-- Detail Modal -->
        <div x-cloak x-show="selectedMessage" 
             class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
             @keydown.escape.window="selectedMessage = null">
            <div class="glass w-full max-w-4xl max-h-[90vh] rounded-3xl overflow-hidden flex flex-col"
                 @click.away="selectedMessage = null">
                <div class="p-6 border-b border-white/10 flex justify-between items-center bg-white/5">
                    <div>
                        <h2 class="text-2xl font-bold" x-text="selectedMessage?.payload?.action_name || 'Message Details'"></h2 >
                        <p class="text-gray-400 text-sm" x-text="'ID: ' + selectedMessage?.id"></p>
                    </div>
                    <button @click="selectedMessage = null" class="p-2 hover:bg-white/10 rounded-full transition-colors">
                        <i data-lucide="x" class="w-6 h-6"></i>
                    </button>
                </div>
                
                <div class="p-8 overflow-y-auto flex-1">
                    <div class="mb-8">
                        <h3 class="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-3">Error Reason</h3>
                        <div class="p-4 rounded-xl border font-mono text-sm"
                             :class="selectedMessage?.reason && (selectedMessage.reason.includes('Insufficient Balance') || selectedMessage.reason.includes('402')) ? 'bg-amber-500/10 border-amber-500/20 text-amber-400' : 'bg-red-500/10 border-red-500/20 text-red-400'"
                             x-text="selectedMessage?.reason"></div>
                    </div>

                    <div>
                        <h3 class="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-3">Payload (JSON)</h3>
                        <div class="relative group">
                            <pre class="p-6 rounded-2xl bg-gray-900/50 border border-white/5 font-mono text-sm overflow-x-auto text-cyan-300"
                                 x-text="JSON.stringify(selectedMessage?.payload, null, 2)"></pre>
                            <button @click="copyText(JSON.stringify(selectedMessage?.payload, null, 2))"
                                    class="absolute top-4 right-4 p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 transition-colors opacity-0 group-hover:opacity-100">
                                    <i data-lucide="copy" class="w-4 h-4"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <div class="p-6 bg-white/5 border-t border-white/10 flex justify-end gap-4">
                    <button @click="deleteMessage(selectedMessage)" 
                            class="px-6 py-2.5 rounded-xl border border-red-500/20 text-red-400 hover:bg-red-500/10 transition-all font-medium">
                        Delete
                    </button>
                    <button @click="copyCommand(selectedMessage)" 
                            class="px-6 py-2.5 rounded-xl glass hover:bg-white/10 transition-all font-medium">
                        Copy Command
                    </button>
                    <button @click="reprocess(selectedMessage)" 
                            class="px-8 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:shadow-[0_0_20px_rgba(79,70,229,0.4)] transition-all font-medium">
                        Reprocess Now
                    </button>
                </div>
            </div>
        </div>

        <!-- Toast Notification -->
        <div x-cloak x-show="toast.show" 
             x-transition:enter="transition ease-out duration-300"
             x-transition:enter-start="opacity-0 translate-y-4"
             x-transition:enter-end="opacity-100 translate-y-0"
             x-transition:leave="transition ease-in duration-200"
             x-transition:leave-start="opacity-100 translate-y-0"
             x-transition:leave-end="opacity-0 translate-y-4"
             class="fixed bottom-8 right-8 z-[100]">
            <div class="glass px-6 py-4 rounded-2xl shadow-2xl flex items-center gap-3 border-l-4 border-indigo-500">
                <i data-lucide="check-circle" class="w-5 h-5 text-indigo-400"></i>
                <span x-text="toast.message"></span>
            </div>
        </div>
    </div>

    <script>
        function dlqApp() {
            return {
                loading: false,
                reprocessingBalance: false,
                messages: [],
                selectedMessage: null,
                toast: { show: false, message: '' },
                stats: [
                    { label: 'Total Failed', value: 0 },
                    { label: 'Collector', value: 0 },
                    { label: 'Processor', value: 0 },
                    { label: 'Newspaper', value: 0 },
                    { label: 'Balance Errors', value: 0 },
                ],

                async fetchMessages() {
                    this.loading = true;
                    try {
                        const response = await fetch('/api/messages');
                        this.messages = await response.json();
                        this.updateStats();
                        setTimeout(() => lucide.createIcons(), 50);
                    } catch (e) {
                        console.error('Fetch failed', e);
                    } finally {
                        this.loading = false;
                    }
                },

                updateStats() {
                    const collector = this.messages.filter(m => m.service === 'data_collector_service').length;
                    const processor = this.messages.filter(m => m.service === 'data_processing_service').length;
                    const newspaper = this.messages.filter(m => m.service === 'newspaper_service').length;
                    const balance = this.messages.filter(m => m.reason && (m.reason.includes('Insufficient Balance') || m.reason.includes('402'))).length;
                    
                    this.stats[0].value = this.messages.length;
                    this.stats[1].value = collector;
                    this.stats[2].value = processor;
                    this.stats[3].value = newspaper;
                    this.stats[4].value = balance;
                },

                formatDate(timestamp) {
                    const date = new Date(parseInt(timestamp));
                    return date.toLocaleString();
                },

                async reprocess(msg) {
                    if (!confirm('Reprocess this message and move it back to the active queue?')) return;
                    
                    try {
                        const response = await fetch(`/api/reprocess/${msg.service}/${msg.id}`, { method: 'POST' });
                        const result = await response.json();
                        
                        if (result.status === 'success') {
                            this.showToast('Message sent to ' + result.target);
                            this.messages = this.messages.filter(m => m.id !== msg.id);
                            this.updateStats();
                            this.selectedMessage = null;
                        }
                    } catch (e) {
                        alert('Reprocessing failed: ' + e.message);
                    }
                },

                async reprocessBalanceErrors() {
                    const balanceErrorCount = this.messages.filter(m => 
                        m.reason && (m.reason.includes('Insufficient Balance') || m.reason.includes('402'))
                    ).length;

                    if (balanceErrorCount === 0) {
                        alert('No insufficient balance errors found in the current DLQ view.');
                        return;
                    }

                    if (!confirm(`Are you sure you want to reprocess all ${balanceErrorCount} commands with "Insufficient Balance" / 402 errors?`)) {
                        return;
                    }

                    this.reprocessingBalance = true;
                    try {
                        const response = await fetch('/api/reprocess-insufficient-balance', { method: 'POST' });
                        const result = await response.json();
                        
                        if (result.status === 'success') {
                            const count = result.reprocessed_count;
                            this.showToast(`Successfully reprocessed ${count} balance-related messages!`);
                            await this.fetchMessages();
                        } else {
                            alert('Reprocessing completed with errors: ' + (result.errors || []).join(', '));
                        }
                    } catch (e) {
                        alert('Bulk reprocessing failed: ' + e.message);
                    } finally {
                        this.reprocessingBalance = false;
                    }
                },

                async deleteMessage(msg) {
                    if (!confirm('Are you sure you want to permanently delete this message from the DLQ?')) return;
                    
                    try {
                        const response = await fetch(`/api/messages/${msg.service}/${msg.id}`, { method: 'DELETE' });
                        const result = await response.json();
                        
                        if (result.status === 'success') {
                            this.showToast('Message deleted successfully');
                            this.messages = this.messages.filter(m => m.id !== msg.id);
                            this.updateStats();
                            this.selectedMessage = null;
                        }
                    } catch (e) {
                        alert('Delete failed: ' + e.message);
                    }
                },

                copyCommand(msg) {
                    const payload = {...msg.payload};
                    if (payload.context) {
                        payload.context.retry_count = 0;
                        payload.context.attempts = [];
                    }
                    const targetService = payload.target_service || msg.service;
                    const newTopic = targetService + ':commands';
                    payload.topic = newTopic;
                    
                    const cleanJson = JSON.stringify(payload);
                    const command = `XADD ${newTopic} * payload '${cleanJson}'`;
                    this.copyText(command);
                    this.showToast('Redis command copied to clipboard!');
                },

                copyText(text) {
                    navigator.clipboard.writeText(text);
                },

                showToast(msg) {
                    this.toast.message = msg;
                    this.toast.show = true;
                    setTimeout(() => this.toast.show = false, 3000);
                }
            }
        }
        
        // Initial icon load
        document.addEventListener('DOMContentLoaded', () => {
            lucide.createIcons();
        });
    </script>
</body>
</html>
"""


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
