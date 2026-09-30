'use client'

import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'

const COLORS = { POSITIVE: '#22c55e', NEGATIVE: '#ef4444' }

export default function Dashboard() {
  const [feedback, setFeedback] = useState([])
  const [topics, setTopics] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      const { data: feedbackData, error: feedbackError } = await supabase
        .from('feedback')
        .select('*')
        .order('created_at', { ascending: false })

      const { data: topicsData, error: topicsError } = await supabase
        .from('topics')
        .select('*')
        .order('review_count', { ascending: false })

      if (feedbackError) console.error('Feedback fetch error:', feedbackError)
      if (topicsError) console.error('Topics fetch error:', topicsError)

      setFeedback(feedbackData || [])
      setTopics(topicsData || [])
      setLoading(false)
    }

    fetchData()
  }, [])

  if (loading) {
    return <div className="flex items-center justify-center h-screen text-lg">Loading insights...</div>
  }

  const sentimentCounts = [
    { name: 'POSITIVE', value: feedback.filter(f => f.sentiment === 'POSITIVE').length },
    { name: 'NEGATIVE', value: feedback.filter(f => f.sentiment === 'NEGATIVE').length },
  ]

  const totalNegative = sentimentCounts.find(s => s.name === 'NEGATIVE')?.value || 0

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Voixa AI — Voice of Customer Insights</h1>
      <p className="text-gray-500 mb-8">{feedback.length} reviews analyzed · {totalNegative} flagged as negative</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Sentiment breakdown */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Sentiment Breakdown</h2>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={sentimentCounts} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
                {sentimentCounts.map((entry, i) => (
                  <Cell key={i} fill={COLORS[entry.name]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Top issues by volume */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Top Recurring Issues</h2>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={topics.slice(0, 8)} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis type="category" dataKey="label" width={140} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="review_count" fill="#ef4444" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Issue table */}
      <div className="bg-white rounded-xl shadow p-6 mb-8">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">All Issue Themes</h2>
        <table className="w-full text-sm text-left">
          <thead>
            <tr className="border-b text-gray-500">
              <th className="py-2 pr-4">Issue</th>
              <th className="py-2 pr-4">Keywords</th>
              <th className="py-2">Reviews</th>
            </tr>
          </thead>
          <tbody>
            {topics.map(t => (
              <tr key={t.id} className="border-b last:border-0">
                <td className="py-2 pr-4 font-medium text-gray-800">{t.label}</td>
                <td className="py-2 pr-4 text-gray-500">{t.keywords}</td>
                <td className="py-2 text-gray-800">{t.review_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Recent negative feedback */}
      <div className="bg-white rounded-xl shadow p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Recent Negative Feedback</h2>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {feedback.filter(f => f.sentiment === 'NEGATIVE').slice(0, 20).map(f => (
            <div key={f.id} className="border-l-4 border-red-400 pl-3 py-1">
              <p className="text-sm text-gray-700">{f.text}</p>
              {f.topic_label && <span className="text-xs text-red-500">Issue: {f.topic_label}</span>}
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}