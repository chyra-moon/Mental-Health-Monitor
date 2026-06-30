import http from './http'

export function analyzeEmotionImage(imageBlob) {
  const formData = new FormData()
  formData.append('file', imageBlob, 'capture.jpg')
  return http.post('/emotion/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}
