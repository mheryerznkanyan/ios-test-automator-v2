'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

interface TestResult {
  test_code: string
  metadata?: {
    quality_report?: {
      overall_score: number
      grade: string
      confidence: string
      recommendations: string[]
    }
  }
}

export default function TestGenerator() {
  const [videoFile, setVideoFile] = useState<File | null>(null)
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<TestResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleGenerate = async () => {
    if (!videoFile || !description) {
      setError('Please provide both a screen recording and test description')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('screen_recording', videoFile)
      formData.append('test_description', description)

      const response = await fetch('/api/tests/generate', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Failed to generate test')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate test')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <header className="border-b border-gray-800 bg-black/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">⚡</span>
            <span className="text-xl font-bold">Testara</span>
          </div>
          <a
            href="https://testara.dev"
            className="text-sm text-gray-400 hover:text-white transition-colors"
          >
            About
          </a>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column: Input */}
          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <h1 className="text-4xl font-bold mb-2">Generate iOS Test</h1>
              <p className="text-gray-400">
                Upload a screen recording and describe what you want to test
              </p>
            </motion.div>

            {/* Screen Recording Upload */}
            <motion.div
              className="glass p-6 rounded-xl"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1, duration: 0.6 }}
            >
              <label className="block text-sm font-semibold mb-3">
                Screen Recording
              </label>
              <div className="border-2 border-dashed border-gray-700 rounded-lg p-8 text-center hover:border-blue-500 transition-colors">
                <input
                  type="file"
                  accept="video/*"
                  onChange={(e) => setVideoFile(e.target.files?.[0] || null)}
                  className="hidden"
                  id="video-upload"
                />
                <label
                  htmlFor="video-upload"
                  className="cursor-pointer flex flex-col items-center gap-2"
                >
                  <svg
                    className="w-12 h-12 text-gray-500"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                    />
                  </svg>
                  {videoFile ? (
                    <span className="text-blue-400">{videoFile.name}</span>
                  ) : (
                    <>
                      <span className="text-gray-400">
                        Click to upload or drag and drop
                      </span>
                      <span className="text-xs text-gray-500">
                        MP4, MOV up to 50MB
                      </span>
                    </>
                  )}
                </label>
              </div>
            </motion.div>

            {/* Test Description */}
            <motion.div
              className="glass p-6 rounded-xl"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.6 }}
            >
              <label className="block text-sm font-semibold mb-3">
                Test Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Example: Test login with invalid password shows error message"
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows={4}
              />
              <p className="text-xs text-gray-500 mt-2">
                Describe what the test should verify in plain English
              </p>
            </motion.div>

            {/* Generate Button */}
            <motion.button
              onClick={handleGenerate}
              disabled={loading || !videoFile || !description}
              className="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-gray-700 disabled:cursor-not-allowed text-white px-8 py-4 rounded-lg text-lg font-semibold transition-all duration-300 hover:scale-105 disabled:hover:scale-100"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.6 }}
              whileHover={{ scale: loading ? 1 : 1.02 }}
              whileTap={{ scale: loading ? 1 : 0.98 }}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg
                    className="animate-spin h-5 w-5"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Generating...
                </span>
              ) : (
                'Generate Test'
              )}
            </motion.button>

            {/* Error Message */}
            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="bg-red-500/10 border border-red-500/50 rounded-lg p-4"
                >
                  <p className="text-red-400 text-sm">{error}</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Right Column: Results */}
          <div className="space-y-6">
            <AnimatePresence mode="wait">
              {result ? (
                <motion.div
                  key="result"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.6 }}
                  className="space-y-6"
                >
                  {/* Quality Score */}
                  {result.metadata?.quality_report && (
                    <div className="glass p-6 rounded-xl">
                      <h3 className="text-lg font-semibold mb-4">Quality Score</h3>
                      <div className="flex items-center gap-4 mb-4">
                        <div className="text-5xl font-bold text-blue-400">
                          {result.metadata.quality_report.grade}
                        </div>
                        <div>
                          <div className="text-2xl font-semibold">
                            {result.metadata.quality_report.overall_score}/100
                          </div>
                          <div className="text-sm text-gray-400">
                            Confidence: {result.metadata.quality_report.confidence}
                          </div>
                        </div>
                      </div>

                      {result.metadata.quality_report.recommendations.length > 0 && (
                        <div>
                          <h4 className="text-sm font-semibold mb-2">
                            Recommendations
                          </h4>
                          <ul className="space-y-1">
                            {result.metadata.quality_report.recommendations.map(
                              (rec, i) => (
                                <li
                                  key={i}
                                  className="text-sm text-gray-400 flex items-start gap-2"
                                >
                                  <span className="text-blue-400 mt-1">•</span>
                                  <span>{rec}</span>
                                </li>
                              )
                            )}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Generated Code */}
                  <div className="glass p-6 rounded-xl">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold">Generated Test</h3>
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(result.test_code)
                        }}
                        className="text-sm text-gray-400 hover:text-white transition-colors flex items-center gap-2"
                      >
                        <svg
                          className="w-4 h-4"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                          />
                        </svg>
                        Copy
                      </button>
                    </div>

                    <div className="rounded-lg overflow-hidden">
                      <SyntaxHighlighter
                        language="swift"
                        style={vscDarkPlus}
                        customStyle={{
                          margin: 0,
                          borderRadius: '0.5rem',
                          fontSize: '0.875rem',
                        }}
                      >
                        {result.test_code}
                      </SyntaxHighlighter>
                    </div>
                  </div>
                </motion.div>
              ) : (
                <motion.div
                  key="placeholder"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="glass p-12 rounded-xl text-center h-full flex items-center justify-center"
                >
                  <div>
                    <div className="text-6xl mb-4">⚡</div>
                    <p className="text-gray-400">
                      Your generated test will appear here
                    </p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </main>
    </div>
  )
}
