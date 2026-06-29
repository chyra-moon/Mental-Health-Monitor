export const emotionMeta = {
  happy: { label: '开心', type: 'success', color: '#4f8f65' },
  sad: { label: '悲伤', type: 'primary', color: '#337f95' },
  angry: { label: '愤怒', type: 'danger', color: '#b95542' },
  fear: { label: '恐惧', type: 'warning', color: '#b8752b' },
  disgust: { label: '厌恶', type: 'info', color: '#7c7268' },
  surprise: { label: '惊讶', type: 'warning', color: '#d4874a' },
  neutral: { label: '平静', type: 'success', color: '#2f9a8d' },
}

export const riskMeta = {
  low: { label: '低风险', type: 'low', tagType: 'success', color: '#4f8f65' },
  medium: { label: '中风险', type: 'medium', tagType: 'warning', color: '#b8752b' },
  high: { label: '高风险', type: 'high', tagType: 'danger', color: '#b95542' },
}

export const emotionKeys = Object.keys(emotionMeta)
export const riskKeys = ['low', 'medium', 'high']
export const negativeEmotions = ['sad', 'angry', 'fear', 'disgust']

export const emotionLabel = (value) => emotionMeta[value]?.label || value || '-'
export const emotionColor = (value) => emotionMeta[value]?.color || '#7c8b86'
export const emotionType = (value) => emotionMeta[value]?.type || 'info'
export const riskLabel = (value) => riskMeta[value]?.label || value || '-'
export const riskTagType = (value) => riskMeta[value]?.tagType || 'info'
export const riskColor = (value) => riskMeta[value]?.color || '#7c8b86'

export const formatTime = (value) => (value ? new Date(value).toLocaleString() : '-')
export const formatPercent = (value) => (value == null ? '-' : `${(value * 100).toFixed(1)}%`)

export function countBy(items, field, keys) {
  const counts = Object.fromEntries(keys.map((key) => [key, 0]))
  items.forEach((item) => {
    if (counts[item[field]] !== undefined) counts[item[field]] += 1
  })
  return counts
}

export function sourceLabel(row) {
  return row.source_label || (row.source_type === 'video' ? '视频分析' : '图片识别')
}

export function sourceBadgeType(value) {
  return value === 'video' ? 'video' : 'image'
}
