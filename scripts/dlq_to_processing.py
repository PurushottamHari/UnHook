import json
import sys


def generate_redis_command():
    print("Paste the DLQ message JSON below and press Enter (Ctrl+D to finish):")
    try:
        # Read all input from stdin
        input_data = sys.stdin.read()
        if not input_data.strip():
            return

        # Parse JSON
        message = json.loads(input_data)

        # 1. Reset retry count and attempts
        if "context" in message:
            message["context"]["retry_count"] = 0
            message["context"]["attempts"] = []

        # 2. Determine target topic (usually {target_service}:commands)
        target_service = message.get("target_service")
        if target_service:
            new_topic = f"{target_service}:commands"
            message["topic"] = new_topic
        else:
            # Fallback logic if target_service is missing
            current_topic = message.get("topic", "")
            if ":dead_letter_queue" in current_topic:
                new_topic = current_topic.replace(":dead_letter_queue", ":commands")
            else:
                new_topic = "unknown_service:commands"
            message["topic"] = new_topic

        # 3. Generate the command
        # separators=(',', ':') removes extra spaces for a more compact command
        clean_json = json.dumps(message, separators=(",", ":"))

        command = f"redis-cli XADD {new_topic} * payload '{clean_json}'"

        print("\n" + "=" * 50)
        print("Generated Redis Command:")
        print("=" * 50 + "\n")
        print(command)
        print("\n" + "=" * 50)

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format. {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    generate_redis_command()
