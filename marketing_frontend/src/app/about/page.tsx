import CTAButton from "@/components/CTAButton";
import TeerthLogo from "@/components/TeerthLogo";
import TeerthLogoIcon from "@/components/TeerthLogoIcon";

export default function About() {
  return (
    <div className="min-h-screen bg-yellow-50 dark:bg-amber-50">
      <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Header Section */}
          <div className="text-center mb-16">
            {/* Teerth Logo */}
            <div className="flex justify-center mb-8">
              <TeerthLogo alt="Teerth Logo" width={200} height={50} />
            </div>
            
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-light text-amber-900 dark:text-amber-900 mb-8 leading-tight tracking-tight">
              Reclaim your attention.
            </h1>
            <p className="text-xl md:text-2xl text-amber-700 dark:text-amber-800 font-light leading-relaxed max-w-4xl mx-auto">
              Daily reads that train your focus instead of draining it.
            </p>
          </div>

          {/* Why This Exists */}
          <div className="mb-16">
            <div className="bg-gradient-to-br from-amber-50/30 to-amber-100/30 dark:from-amber-100/30 dark:to-amber-200/30 rounded-3xl p-8 md:p-12 border border-amber-200/20 dark:border-amber-300/20 backdrop-blur-sm shadow-lg">
              <h2 className="text-3xl md:text-4xl font-light text-amber-900 dark:text-amber-900 mb-6 flex items-center gap-3">
                <span className="text-4xl">🌱</span>
                Why This Exists
              </h2>
              <div className="prose prose-lg max-w-none text-amber-800 dark:text-amber-900">
                <p className="text-lg leading-relaxed mb-6">
                  Apps today are built to hijack your attention: infinite scrolls, outrage-bait, passive feeds that numb you, and systems that profit from your screen time, not your growth.
                </p>
                <p className="text-lg leading-relaxed">
                  We think that's broken. We're building something different — a space that helps you read, think, and get sharper every day.
                </p>
              </div>
            </div>
          </div>

          {/* Divider */}
          <div className="flex justify-center mb-16">
            <div className="w-24 h-px bg-amber-300 dark:bg-amber-400"></div>
          </div>

          {/* What's Broken */}
          <div className="mb-16">
            <div className="bg-gradient-to-br from-amber-50/30 to-amber-100/30 dark:from-amber-100/30 dark:to-amber-200/30 rounded-3xl p-8 md:p-12 border border-amber-200/20 dark:border-amber-300/20 backdrop-blur-sm shadow-lg">
              <h2 className="text-3xl md:text-4xl font-light text-amber-900 dark:text-amber-900 mb-8 flex items-center gap-3">
                <span className="text-4xl">🚨</span>
                What's Broken
              </h2>
              <ul className="space-y-4 text-amber-800 dark:text-amber-900">
                <li className="flex items-start gap-3">
                  <span className="text-amber-600 dark:text-amber-700 mt-1">•</span>
                  <span className="text-lg leading-relaxed"><strong>Infinite scroll</strong> — keeps you stuck, never satisfied.</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-amber-600 dark:text-amber-700 mt-1">•</span>
                  <span className="text-lg leading-relaxed"><strong>Emotional clickbait</strong> — provokes unnecessary reactions to hook you.</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-amber-600 dark:text-amber-700 mt-1">•</span>
                  <span className="text-lg leading-relaxed"><strong>Passive consumption</strong> — feeds that don't train your memory or reasoning.</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-amber-600 dark:text-amber-700 mt-1">•</span>
                  <span className="text-lg leading-relaxed"><strong>Attention = currency</strong> — products reward time wasted, not progress made.</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-amber-600 dark:text-amber-700 mt-1">•</span>
                  <span className="text-lg leading-relaxed"><strong>Scattered sources</strong> — knowledge is everywhere but rarely stitched together.</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Divider */}
          <div className="flex justify-center mb-16">
            <div className="w-24 h-px bg-amber-300 dark:bg-amber-400"></div>
          </div>

          {/* Why Fighting Feeds Doesn't Work */}
          <div className="mb-16">
            <div className="bg-gradient-to-br from-amber-50/30 to-amber-100/30 dark:from-amber-100/30 dark:to-amber-200/30 rounded-3xl p-8 md:p-12 border border-amber-200/20 dark:border-amber-300/20 backdrop-blur-sm shadow-lg">
              <h2 className="text-3xl md:text-4xl font-light text-amber-900 dark:text-amber-900 mb-6 flex items-center gap-3">
                <span className="text-4xl">💣</span>
                Why Fighting Feeds Doesn't Work
              </h2>
              <div className="prose prose-lg max-w-none text-amber-800 dark:text-amber-900">
                <p className="text-lg leading-relaxed mb-6">
                  These algorithms aren't neutral. They're built to hack your brain and drag you into doomscroll loops again and again. Fighting them is like walking through a minefield — eventually, you'll get caught.
                </p>
                <p className="text-lg leading-relaxed">
                  Instead, bring your favorite sources here and get a clean, non-toxic feed where the content works for you.
                </p>
              </div>
            </div>
          </div>

          {/* Divider */}
          <div className="flex justify-center mb-16">
            <div className="w-24 h-px bg-amber-300 dark:bg-amber-400"></div>
          </div>

          {/* How We Fix It */}
          <div className="mb-16">
            <div className="bg-gradient-to-br from-amber-50/30 to-amber-100/30 dark:from-amber-100/30 dark:to-amber-200/30 rounded-3xl p-8 md:p-12 border border-amber-200/20 dark:border-amber-300/20 backdrop-blur-sm shadow-lg">
              <h2 className="text-3xl md:text-4xl font-light text-amber-900 dark:text-amber-900 mb-8 flex items-center gap-3">
                <span className="text-4xl">✨</span>
                How We Fix It
              </h2>
              <div className="space-y-6 text-amber-800 dark:text-amber-900">
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="md:w-1/3">
                    <span className="text-lg font-semibold text-amber-700 dark:text-amber-800">Infinite scroll</span>
                  </div>
                  <div className="md:w-2/3">
                    <span className="text-lg">→ Daily editions.<br/>A curated paper (3–5 articles) sized to your time. No endless feeds.</span>
                  </div>
                </div>
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="md:w-1/3">
                    <span className="text-lg font-semibold text-amber-700 dark:text-amber-800">Clickbait</span>
                  </div>
                  <div className="md:w-2/3">
                    <span className="text-lg">→ Honest, meaningful headlines.<br/>Designed to inform, not manipulate.</span>
                  </div>
                </div>
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="md:w-1/3">
                    <span className="text-lg font-semibold text-amber-700 dark:text-amber-800">Passive consumption</span>
                  </div>
                  <div className="md:w-2/3">
                    <span className="text-lg">→ Active engagement.<br/>Short insights, recall quizzes, and reflective prompts to turn reading into practice.</span>
                  </div>
                </div>
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="md:w-1/3">
                    <span className="text-lg font-semibold text-amber-700 dark:text-amber-800">Attention ≠ revenue</span>
                  </div>
                  <div className="md:w-2/3">
                    <span className="text-lg">→ Respectful design.<br/>No dark patterns, no engagement-maximizing tricks.</span>
                  </div>
                </div>
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="md:w-1/3">
                    <span className="text-lg font-semibold text-amber-700 dark:text-amber-800">Scattered sources</span>
                  </div>
                  <div className="md:w-2/3">
                    <span className="text-lg">→ Your curated mix.<br/>Connect YouTube, Reddit, news, blogs — and you choose what belongs in your paper.</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Divider */}
          <div className="flex justify-center mb-16">
            <div className="w-24 h-px bg-amber-300 dark:bg-amber-400"></div>
          </div>

          {/* What We're Building */}
          <div className="mb-16">
            <div className="bg-gradient-to-br from-amber-50/30 to-amber-100/30 dark:from-amber-100/30 dark:to-amber-200/30 rounded-3xl p-8 md:p-12 border border-amber-200/20 dark:border-amber-300/20 backdrop-blur-sm shadow-lg">
              <h2 className="text-3xl md:text-4xl font-light text-amber-900 dark:text-amber-900 mb-8 flex items-center gap-3">
                <span className="text-4xl">🚀</span>
                What We're Building
              </h2>
              <ul className="space-y-4 text-amber-800 dark:text-amber-900">
                <li className="flex items-start gap-3">
                  <span className="text-amber-600 dark:text-amber-700 mt-1">•</span>
                  <span className="text-lg leading-relaxed">Personalized newspaper tailored to your interests.</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-amber-600 dark:text-amber-700 mt-1">•</span>
                  <span className="text-lg leading-relaxed">Reading-time modes (Quick / Mid / Deep).</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-amber-600 dark:text-amber-700 mt-1">•</span>
                  <span className="text-lg leading-relaxed">Honest curation and clear choices — you decide what's worth your time.</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-amber-600 dark:text-amber-700 mt-1">•</span>
                  <span className="text-lg leading-relaxed">AI tools that don't steal your focus — they help you grow it.</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-amber-600 dark:text-amber-700 mt-1">•</span>
                  <span className="text-lg leading-relaxed">Over time, your daily reads + AI-driven questions will make your mind stronger, sharper, and more focused.</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Waitlist Section */}
          <div className="bg-gradient-to-br from-amber-100/80 to-amber-200/80 dark:from-amber-200/80 dark:to-amber-300/80 rounded-3xl shadow-2xl border border-amber-200/50 dark:border-amber-300/50 p-8 md:p-12 backdrop-blur-sm">
            <div className="flex flex-col lg:flex-row gap-8 lg:gap-16">
              {/* Left side - Text content */}
              <div className="w-full lg:w-[35%]">
                <h3 className="text-3xl md:text-4xl font-light text-amber-900 dark:text-amber-900 mb-6 leading-tight">
                  Ready to Reclaim Your Attention?
                </h3>
                <p className="text-lg text-amber-800 dark:text-amber-900 mb-8 font-light leading-relaxed">
                  Join the waitlist and be among the first to experience a different kind of reading:
                </p>
                <ul className="space-y-3">
                  <li className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-6 h-6 mt-0.5">
                      <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <span className="text-amber-800 dark:text-amber-900">No infinite scrolls or clickbait</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-6 h-6 mt-0.5">
                      <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    </div>
                    <span className="text-amber-800 dark:text-amber-900">Active engagement, not passive consumption</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-6 h-6 mt-0.5">
                      <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <span className="text-amber-800 dark:text-amber-900">Your curated mix of sources</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-6 h-6 mt-0.5">
                      <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <span className="text-amber-800 dark:text-amber-900">AI that helps you grow, not distract</span>
                  </li>
                </ul>
                
                {/* Teerth Logo Icon under features */}
                <div className="flex justify-center mt-6">
                  <TeerthLogoIcon alt="Teerth Logo Icon" width={75} height={50} />
                </div>
              </div>

              {/* Divider */}
              <div className="hidden lg:block w-px bg-amber-300 dark:bg-amber-400"></div>

              {/* Right side - Form */}
              <div className="w-full lg:w-[60%]">
                <form className="max-w-md mx-auto lg:mx-0">
                  <div className="mb-6">
                    <input
                      type="email"
                      placeholder="Enter your email address"
                      className="w-full px-6 py-4 border border-amber-300/50 dark:border-amber-400/50 rounded-2xl focus:ring-2 focus:ring-amber-500/50 focus:border-transparent dark:bg-amber-200/50 dark:text-amber-900 placeholder-amber-600/70 bg-white/50 backdrop-blur-sm text-lg font-light transition-all duration-300 hover:border-amber-400/70"
                      required
                    />
                  </div>
                  <div className="mb-6">
                    <textarea
                      placeholder="What sources do you want to see in your daily paper?"
                      rows={4}
                      className="w-full px-6 py-4 border border-amber-300/50 dark:border-amber-400/50 rounded-2xl focus:ring-2 focus:ring-amber-500/50 focus:border-transparent dark:bg-amber-200/50 dark:text-amber-900 placeholder-amber-600/70 bg-white/50 backdrop-blur-sm text-lg font-light resize-none transition-all duration-300 hover:border-amber-400/70"
                    />
                  </div>
                  <button
                    type="submit"
                    className="w-full bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-700 hover:to-amber-800 text-white font-light py-4 px-8 rounded-2xl transition-all duration-300 text-lg shadow-lg hover:shadow-xl transform hover:scale-[1.02] mb-4"
                  >
                    Join Waitlist
                  </button>
                  <CTAButton 
                    href="/dashboard" 
                    variant="secondary" 
                    size="lg"
                    className="w-full bg-amber-100 hover:bg-amber-200 text-amber-800 hover:text-amber-900 border border-amber-300 hover:border-amber-400"
                  >
                    Preview Dashboard
                  </CTAButton>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
