export const EMOTION_KEYS = ['happy', 'sad', 'angry', 'fear', 'disgust', 'surprise', 'neutral'];

export const EMOTION_META = {
  happy: { label: '开心', color: '#10b981' },     // Green
  sad: { label: '悲伤', color: '#3b82f6' },       // Blue
  angry: { label: '愤怒', color: '#ef4444' },     // Red
  fear: { label: '恐惧', color: '#8b5cf6' },      // Purple
  disgust: { label: '厌恶', color: '#f59e0b' },    // Amber
  surprise: { label: '惊讶', color: '#ec4899' },   // Pink
  neutral: { label: '平静', color: '#64748b' }     // Slate
};

export const NEGATIVE_EMOTIONS = new Set(['sad', 'angry', 'fear', 'disgust']);

export const RISK_META = {
  low: { label: '低风险', type: 'success', color: '#10b981' },
  medium: { label: '中风险', type: 'warning', color: '#f59e0b' },
  high: { label: '高风险', type: 'danger', color: '#ef4444' }
};

export function emotionLabel(emotion) {
  return EMOTION_META[emotion]?.label || emotion || '-';
}

export function emotionColor(emotion) {
  return EMOTION_META[emotion]?.color || '#64748b';
}

export function riskLabel(level) {
  return RISK_META[level]?.label || level || '-';
}

export function riskType(level) {
  return RISK_META[level]?.type || 'info';
}

export function riskColor(level) {
  return RISK_META[level]?.color || '#64748b';
}

export function formatTime(value) {
  if (!value) return '-';
  const date = new Date(value);
  if (isNaN(date.getTime())) return value;
  
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  const hh = String(date.getHours()).padStart(2, '0');
  const mm = String(date.getMinutes()).padStart(2, '0');
  const ss = String(date.getSeconds()).padStart(2, '0');
  
  return `${y}-${m}-${d} ${hh}:${mm}:${ss}`;
}
