'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Navigation from '@/components/Navigation'

interface Settings {
  device: string
  iosVersion: string
  appName: string
}

const AVAILABLE_DEVICES = [
  'iPhone 17 Pro',
  'iPhone 16 Pro Max',
  'iPhone 16 Pro',
  'iPhone 15 Pro Max',
  'iPhone 15 Pro',
  'iPhone 15',
  'iPhone 14 Pro',
  'iPhone 14',
  'iPhone 13',
  'iPhone SE (3rd generation)',
]

const AVAILABLE_IOS_VERSIONS = [
  '18.0',
  '17.5',
  '17.4',
  '17.2',
  '17.1',
  '17.0',
  '16.4',
  '16.0',
  '15.0',
]

export default function SettingsPage() {
  const [settings, setSettings] = useState<Settings>({
    device: 'iPhone 15 Pro',
    iosVersion: '17.0',
    appName: 'YourApp',
  })
  
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    // Load settings from localStorage
    const stored = localStorage.getItem('testara_settings')
    if (stored) {
      setSettings(JSON.parse(stored))
    }
  }, [])

  const handleSave = () => {
    localStorage.setItem('testara_settings', JSON.stringify(settings))
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="min-h-screen bg-black">
      <Navigation />
      
      <main className="max-w-3xl mx-auto px-6 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl font-bold mb-2">Settings</h1>
          <p className="text-gray-400 mb-8">
            Configure simulator and test execution preferences
          </p>
        </motion.div>

        <div className="space-y-6">
          {/* Simulator Device */}
          <motion.div
            className="glass p-6 rounded-xl"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.6 }}
          >
            <label className="block text-sm font-semibold mb-3">
              Simulator Device
            </label>
            <select
              value={settings.device}
              onChange={(e) => setSettings({ ...settings, device: e.target.value })}
              className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {AVAILABLE_DEVICES.map((device) => (
                <option key={device} value={device}>
                  {device}
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-2">
              Select which iPhone simulator to use for test execution
            </p>
          </motion.div>

          {/* iOS Version */}
          <motion.div
            className="glass p-6 rounded-xl"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
          >
            <label className="block text-sm font-semibold mb-3">
              iOS Version
            </label>
            <select
              value={settings.iosVersion}
              onChange={(e) => setSettings({ ...settings, iosVersion: e.target.value })}
              className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {AVAILABLE_IOS_VERSIONS.map((version) => (
                <option key={version} value={version}>
                  iOS {version}
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-2">
              iOS version for the simulator
            </p>
          </motion.div>

          {/* App Name */}
          <motion.div
            className="glass p-6 rounded-xl"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            <label className="block text-sm font-semibold mb-3">
              App Name
            </label>
            <input
              type="text"
              value={settings.appName}
              onChange={(e) => setSettings({ ...settings, appName: e.target.value })}
              placeholder="YourApp"
              className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-2">
              Name of the app being tested (used in test context)
            </p>
          </motion.div>

          {/* Available Simulators Info */}
          <motion.div
            className="glass p-6 rounded-xl"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
          >
            <h3 className="text-sm font-semibold mb-3">Available Simulators</h3>
            <p className="text-sm text-gray-400 mb-3">
              To see which simulators are installed on your machine:
            </p>
            <code className="block bg-gray-900 p-3 rounded text-xs text-green-400 font-mono">
              xcrun simctl list devices available
            </code>
            <p className="text-xs text-gray-500 mt-3">
              Run this command in Terminal to see all available devices
            </p>
          </motion.div>

          {/* Save Button */}
          <motion.button
            onClick={handleSave}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-all duration-300 hover:scale-105"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.6 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {saved ? '✓ Saved!' : 'Save Settings'}
          </motion.button>
        </div>
      </main>
    </div>
  )
}
