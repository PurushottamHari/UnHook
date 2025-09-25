"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import CTAButton from "@/components/CTAButton";
import TeerthLogo from "@/components/TeerthLogo";

interface ProblemCardProps {
  card: {
    front: string;
    back: string;
    icon: string;
  };
  variants: any;
}

function ProblemCard({ card, variants }: ProblemCardProps) {
  const [isRevealed, setIsRevealed] = useState(false);

  const handleToggle = () => {
    setIsRevealed(!isRevealed);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleToggle();
    }
  };

  return (
    <motion.div
      variants={variants}
      className="relative"
    >
      <motion.button
        role="button"
        tabIndex={0}
        aria-expanded={isRevealed}
        aria-label={`${card.front}. Click to reveal more details.`}
        onClick={handleToggle}
        onKeyDown={handleKeyDown}
        className="w-full min-h-[180px] p-6 rounded-2xl cursor-pointer text-left focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:ring-offset-2 relative group"
        whileHover={{ y: -1, scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
        transition={{ duration: 0.2, ease: "easeOut" }}
      >
        {/* Subtle tap indicator */}
        <div className="absolute top-3 right-3 text-amber-400/40 group-hover:text-amber-400/60 transition-all duration-300">
          <div className="w-1.5 h-1.5 rounded-full bg-current opacity-60 group-hover:opacity-80 transition-opacity duration-300"></div>
        </div>

        {/* Front Side - Illusion */}
        <motion.div
          className="w-full h-full flex flex-col items-center justify-center text-center"
          style={{ 
            background: 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(254,243,199,0.7) 100%)',
            border: '1px solid rgba(251,191,36,0.3)',
            boxShadow: '0 4px 20px rgba(251,191,36,0.1)'
          }}
          animate={{ 
            opacity: isRevealed ? 0 : 1,
            y: isRevealed ? -10 : 0
          }}
          transition={{ duration: 0.4, ease: "easeOut" }}
        >
          <div className="text-2xl mb-3">🌀</div>
          <div className="text-xs text-amber-600/70 font-medium mb-2 tracking-wide">
            Feels like...
          </div>
          <p className="text-base text-amber-800 font-light leading-relaxed px-2 mb-3">
            {card.front}
          </p>
          <div className="text-lg opacity-60">
            {card.icon}
          </div>
        </motion.div>

        {/* Back Side - Reality */}
        <motion.div
          className="absolute inset-0 w-full h-full flex flex-col items-center justify-center text-center p-6 rounded-2xl"
          style={{ 
            background: 'linear-gradient(135deg, rgba(248,250,252,0.95) 0%, rgba(241,245,249,0.9) 100%)',
            border: '1px solid rgba(148,163,184,0.3)',
            boxShadow: '0 6px 24px rgba(0,0,0,0.08), inset 0 1px 0 rgba(255,255,255,0.5)'
          }}
          animate={{ 
            opacity: isRevealed ? 1 : 0,
            y: isRevealed ? 0 : 10
          }}
          transition={{ duration: 0.4, ease: "easeOut" }}
        >
          <div className="text-2xl mb-3">🔍</div>
          <div className="text-xs text-slate-600/70 font-medium mb-2 tracking-wide">
            In reality...
          </div>
          <motion.p 
            className="text-sm text-slate-700 font-medium leading-relaxed px-2"
            initial={{ opacity: 0, y: 5 }}
            animate={{ 
              opacity: isRevealed ? 1 : 0,
              y: isRevealed ? 0 : 5
            }}
            transition={{ 
              duration: 0.5, 
              delay: isRevealed ? 0.2 : 0,
              ease: "easeOut"
            }}
          >
            {card.back}
          </motion.p>
        </motion.div>
      </motion.button>
    </motion.div>
  );
}

export default function About() {
  const [showAfter, setShowAfter] = useState(false);

  const fadeInUp = {
    initial: { opacity: 0, y: 60 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.6, ease: "easeOut" }
  };

  const staggerChildren = {
    animate: {
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const fadeInLines = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.8, ease: "easeOut" }
  };

  return (
    <div className="min-h-screen bg-yellow-50 dark:bg-amber-50">
      <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Hero Section */}
          <motion.div 
            className="text-center mb-16"
            initial="initial"
            animate="animate"
            variants={fadeInUp}
          >
            <div className="flex justify-center mb-8">
              <TeerthLogo alt="Teerth Logo" size={200} />
            </div>
            
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-light text-amber-900 dark:text-amber-900 mb-8 leading-tight tracking-tight">
              🌱 Reclaim your attention.
            </h1>
            <p className="text-xl md:text-2xl text-amber-700 dark:text-amber-800 font-light leading-relaxed max-w-4xl mx-auto mb-8">
              Daily reads that sharpen focus instead of scatter it.
            </p>
            <CTAButton 
              href="/dashboard" 
              variant="primary" 
              size="lg"
              className="bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-700 hover:to-amber-800 text-white font-light py-4 px-8 rounded-2xl transition-all duration-300 text-lg shadow-lg hover:shadow-xl transform hover:scale-[1.02]"
            >
              Join the Waitlist → Help Shape Teerth
            </CTAButton>
          </motion.div>

          {/* The Problem Section */}
          <motion.section 
            id="problem"
            className="mb-16"
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            variants={fadeInUp}
          >
            <div className="relative bg-gradient-to-br from-amber-50/30 to-amber-100/30 dark:from-amber-100/30 dark:to-amber-200/30 rounded-3xl p-8 md:p-12 border border-amber-200/20 dark:border-amber-300/20 backdrop-blur-sm shadow-lg overflow-hidden">
              <h2 className="text-3xl md:text-4xl font-light text-amber-900 dark:text-amber-900 mb-4 text-center">
                The Problem With Feeds
              </h2>
              
              <p className="text-lg text-amber-700 dark:text-amber-800 font-light text-center mb-8">
                Social, video, and news feeds — endless streams designed to grab your attention.
              </p>
              
              <motion.div 
                className="flex flex-col items-center gap-6 mb-6 relative z-10"
                variants={staggerChildren}
              >
                {/* Top row - 3 cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl">
                  {[
                    {
                      front: "I'm always learning something new.",
                      back: "But how much of this sticks? Am I truly reflecting — or just skimming, collecting fleeting knowledge?",
                      icon: "🧠"
                    },
                    {
                      front: "Endless scroll gives me choice.",
                      back: "It sparks craving and leaves me empty. The more I scroll, the less satisfied I feel.",
                      icon: "🔄"
                    },
                    {
                      front: "I feel happy and relaxed while scrolling.",
                      back: "But am I running from my real emotions — numbing what needs attention? Who's quietly keeping me hooked to this fleeting relief?",
                      icon: "🌿"
                    }
                  ].map((card, index) => (
                    <ProblemCard key={index} card={card} variants={fadeInUp} />
                  ))}
                </div>
                
                {/* Bottom row - 3 cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl">
                  {[
                    {
                      front: "Feeds surprise me with exciting, edgy content.",
                      back: "But much of it is engineered provocation — sexual, shocking, or agitating — designed to hijack emotion, not nurture focus or clarity.",
                      icon: "🎭"
                    },
                    {
                      front: "It helps me stay informed.",
                      back: "But is it neutral facts, or am I being provoked constantly to react?",
                      icon: "📰"
                    },
                    {
                      front: "Feeds keep me connected.",
                      back: "Yet in real life, I feel lonelier, more divided, subtly provoked — connection feels shallow.",
                      icon: "🤝"
                    }
                  ].map((card, index) => (
                    <ProblemCard key={index + 3} card={card} variants={fadeInUp} />
                  ))}
                </div>
              </motion.div>
              
              <motion.p 
                className="text-sm text-amber-600/70 dark:text-amber-700/70 text-center font-light mb-6"
                initial={{ opacity: 0.7 }}
                animate={{ opacity: 0.7 }}
                transition={{ duration: 0.3 }}
              >
                Click or tap cards to flip and reveal the reality behind each illusion.
              </motion.p>
              
              <motion.div 
                className="mt-12 mb-4"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8, ease: "easeOut" }}
              >
                <motion.p 
                  className="text-xl md:text-2xl lg:text-3xl text-amber-900 dark:text-amber-900 font-light leading-relaxed text-center italic max-w-4xl mx-auto"
                  initial={{ opacity: 0 }}
                  whileInView={{ opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 1.2, delay: 0.3, ease: "easeOut" }}
                >
                  "Feeds feel like they serve us — but on retrospection, they quietly shape habits we didn't choose."
                </motion.p>
              </motion.div>
            </div>
          </motion.section>

          {/* Divider */}
          <div className="flex justify-center mb-16">
            <div className="w-24 h-px bg-amber-300 dark:bg-amber-400"></div>
          </div>

          {/* We Need Something Section */}
          <motion.div 
            className="mb-16"
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            variants={fadeInUp}
          >
            <div className="bg-gradient-to-br from-amber-50/30 to-amber-100/30 dark:from-amber-100/30 dark:to-amber-200/30 rounded-3xl p-8 md:p-12 border border-amber-200/20 dark:border-amber-300/20 backdrop-blur-sm shadow-lg">
              <h2 className="text-3xl md:text-4xl font-bold text-amber-900 dark:text-amber-900 mb-6 text-center">
                We need something that respects our attention.
              </h2>
              
              <div className="text-center mb-12">
                <p className="text-lg text-amber-800 dark:text-amber-900 font-light leading-relaxed italic">
                  This isn't just a patch. It's the first step toward a future where our digital habits serve us — not the other way around.
                </p>
              </div>

              <motion.div 
                className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12"
                variants={staggerChildren}
              >
                {[
                  {
                    step: 1,
                    title: "Start with what matters to you",
                    text: "Choose the themes you care about — science, business, health, art, spirituality, whatever fuels your curiosity. If you'd like, connect your current sources (YouTube channels, Instagram pages, Subreddits, news feeds). These serve as raw material, not distractions.",
                    icon: "🎯"
                  },
                  {
                    step: 2,
                    title: "Get clarity, not noise",
                    text: "No more endless feeds. Instead, you'll get a crisp daily digest: factual, concise updates with no clickbait or emotional provocation. Limited and focused, so you stay informed while keeping your time and energy for what really matters.",
                    icon: "📜"
                  },
                  {
                    step: 3,
                    title: "Refine, reflect, grow",
                    text: "Your digest adapts as you do. Highlight what's helpful, skip what isn't, and it will adjust. You'll be nudged to check what you recall, reflect on insights, and engage with thoughtful prompts that help you analyze, connect, and apply what you've read. Over time, fleeting information turns into lasting clarity and focus.",
                    icon: "🌱"
                  }
                ].map((item, index) => (
                  <motion.div
                    key={index}
                    className="text-center p-8 rounded-2xl bg-white/50 dark:bg-amber-100/50 border border-amber-200/30 dark:border-amber-300/30 hover:shadow-lg hover:scale-[1.02] transition-all duration-300"
                    whileHover={{ y: -2 }}
                    variants={fadeInUp}
                  >
                    <div className="text-4xl mb-4">{item.icon}</div>
                    <div className="text-lg font-bold text-amber-800 dark:text-amber-900 mb-3">
                      Step {item.step} – {item.title}
                    </div>
                    <p className="text-base text-amber-700 dark:text-amber-800 font-light leading-relaxed">
                      {item.text}
                    </p>
                  </motion.div>
                ))}
              </motion.div>

              {/* Divider line */}
              <div className="flex justify-center mb-8">
                <div className="w-32 h-px bg-amber-300 dark:bg-amber-400"></div>
              </div>

              <div className="text-center">
                <p className="text-lg font-bold text-amber-800 dark:text-amber-900 leading-relaxed">
                  📌 This is where it begins
                </p>
                <p className="text-base text-amber-700 dark:text-amber-800 font-light leading-relaxed mt-2">
                  The foundation of healthier digital habits — one step now, many more ahead.
                </p>
              </div>
            </div>
          </motion.div>

          {/* Divider */}
          <div className="flex justify-center mb-16">
            <div className="w-24 h-px bg-amber-300 dark:bg-amber-400"></div>
          </div>

          {/* The Transformation Section */}
          <motion.div 
            className="mb-16"
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            variants={fadeInUp}
          >
            <div className={`rounded-3xl p-8 md:p-12 border backdrop-blur-sm shadow-lg transition-all duration-700 ${
              showAfter 
                ? 'bg-gradient-to-br from-amber-50/30 to-amber-100/30 dark:from-amber-100/30 dark:to-amber-200/30 border-amber-200/20 dark:border-amber-300/20' 
                : 'bg-gradient-to-br from-red-50/30 to-orange-100/30 dark:from-red-100/30 dark:to-orange-200/30 border-red-200/20 dark:border-orange-300/20'
            }`}>
              <h2 className="text-3xl md:text-4xl font-light text-amber-900 dark:text-amber-900 mb-8 text-center">
                The Transformation
              </h2>
              
              {/* Toggle */}
              <div className="flex justify-center mb-8">
                <div className="bg-white/50 dark:bg-amber-100/50 rounded-full p-1 border border-amber-200/30 dark:border-amber-300/30">
                  <button
                    onClick={() => setShowAfter(false)}
                    className={`px-6 py-2 rounded-full transition-all duration-300 ${
                      !showAfter 
                        ? 'bg-red-500 text-white shadow-lg' 
                        : 'text-amber-800 dark:text-amber-900 hover:bg-amber-100/50'
                    }`}
                  >
                    Before
                  </button>
                  <button
                    onClick={() => setShowAfter(true)}
                    className={`px-6 py-2 rounded-full transition-all duration-300 ${
                      showAfter 
                        ? 'bg-amber-600 text-white shadow-lg' 
                        : 'text-amber-800 dark:text-amber-900 hover:bg-amber-100/50'
                    }`}
                  >
                    After
                  </button>
                </div>
              </div>

              <motion.div 
                className="text-center"
                key={showAfter ? 'after' : 'before'}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <div className={`p-8 rounded-2xl border mb-6 transition-all duration-700 ${
                  showAfter 
                    ? 'bg-white/50 dark:bg-amber-100/50 border-amber-200/30 dark:border-amber-300/30' 
                    : 'bg-white/50 dark:bg-red-100/50 border-red-200/30 dark:border-orange-300/30'
                }`}>
                  <p className={`text-2xl font-light leading-relaxed transition-colors duration-700 ${
                    showAfter 
                      ? 'text-amber-800 dark:text-amber-900' 
                      : 'text-red-800 dark:text-red-900'
                  }`}>
                    {showAfter 
                      ? "Calm, intentional, and restorative — a space designed to let the mind pause, reflect, and gain clarity. Every element encourages healing, understanding, and deeper insight."
                      : "Overstimulated, frustrated, and drained — endless feeds that provoked more stress than insight. Content felt scattered, leaving attention fragmented and emotions unsettled."
                    }
                  </p>
                </div>
                
                <p className="text-xl text-amber-800 dark:text-amber-900 font-light leading-relaxed">
                  Imagine shifting from scattered to centered.
                </p>
              </motion.div>
            </div>
          </motion.div>

          {/* Divider */}
          <div className="flex justify-center mb-16">
            <div className="w-24 h-px bg-amber-300 dark:bg-amber-400"></div>
          </div>

          {/* Final CTA Section */}
          <motion.div 
            className="bg-gradient-to-br from-amber-100/80 to-amber-200/80 dark:from-amber-200/80 dark:to-amber-300/80 rounded-3xl shadow-2xl border border-amber-200/50 dark:border-amber-300/50 p-8 md:p-12 backdrop-blur-sm"
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            variants={fadeInUp}
          >
            <div className="text-center">
              <h3 className="text-3xl md:text-4xl font-light text-amber-900 dark:text-amber-900 mb-6 leading-tight">
                ⚡ Join us, don't just sign up.
              </h3>
              <p className="text-lg text-amber-800 dark:text-amber-900 mb-8 font-light leading-relaxed">
                Help shape Teerth. Share ideas. Be part of the waitlist.
              </p>
              <CTAButton 
                href="/dashboard" 
                variant="primary" 
                size="lg"
                className="bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-700 hover:to-amber-800 text-white font-light py-4 px-8 rounded-2xl transition-all duration-300 text-lg shadow-lg hover:shadow-xl transform hover:scale-[1.02]"
              >
                Join the Waitlist → Help Us Build This
              </CTAButton>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
