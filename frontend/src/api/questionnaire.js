import http from './http'

export function getQuestions() {
  return http.get('/questionnaire/questions')
}

export function submitAnswers(answers) {
  return http.post('/questionnaire/submit', answers)
}
