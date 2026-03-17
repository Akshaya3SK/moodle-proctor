const API_BASE_URL = 'http://localhost:5000'

let examTimerId = null
let questionPaperUrl = null

function getStoredSession() {
  const rawSession = localStorage.getItem('authSession')

  if (!rawSession) {
    return null
  }

  try {
    return JSON.parse(rawSession)
  } catch (error) {
    clearSession()
    return null
  }
}

function clearSession() {
  localStorage.removeItem('authSession')
  localStorage.removeItem('token')
}

function redirectToLogin(message) {
  if (message) {
    sessionStorage.setItem('authRedirectMessage', message)
  }

  window.location = 'login.html'
}

function setExamStatus(message, type = 'info') {
  const status = document.getElementById('examMessage')

  if (!status) {
    return
  }

  status.hidden = !message
  status.className = `status-message ${type}`
  status.innerText = message || ''
}

function formatDuration(totalSeconds) {
  const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, '0')
  const seconds = String(totalSeconds % 60).padStart(2, '0')
  return `${minutes}:${seconds}`
}

async function fetchWithSession(url, options = {}) {
  const session = getStoredSession()

  if (!session || !session.token) {
    redirectToLogin('Please sign in before opening the exam.')
    return null
  }

  const response = await fetch(url, {
    ...options,
    headers: {
      ...(options.headers || {}),
      Authorization: `Bearer ${session.token}`
    }
  })

  if (response.status === 401) {
    clearSession()
    redirectToLogin('Your session expired. Please sign in again.')
    return null
  }

  return response
}

function renderExamHeader(student) {
  document.getElementById('examStudentName').innerText = student.name
  document.getElementById('examStudentEmail').innerText = student.email
  document.getElementById('examTitle').innerText = student.exam
}

function completeExam() {
  if (examTimerId) {
    clearInterval(examTimerId)
    examTimerId = null
  }

  document.body.innerHTML = `
    <div class="completion-screen">
      <div class="completion-card">
        <h1>Exam Completed</h1>
        <p>Your exam session has ended successfully.</p>
      </div>
    </div>
  `
}

function startTimer(totalSeconds) {
  const timerElement = document.getElementById('timer')
  let remainingSeconds = totalSeconds

  timerElement.innerText = formatDuration(remainingSeconds)

  examTimerId = setInterval(() => {
    remainingSeconds -= 1

    if (remainingSeconds < 0) {
      completeExam()
      return
    }

    timerElement.innerText = formatDuration(remainingSeconds)
  }, 1000)
}

async function loadQuestionPaper(questionPaperName) {
  const response = await fetchWithSession(`${API_BASE_URL}/files/${questionPaperName}`)

  if (!response) {
    return
  }

  if (!response.ok) {
    throw new Error('Question paper request failed')
  }

  const fileBlob = await response.blob()
  questionPaperUrl = URL.createObjectURL(fileBlob)
  document.getElementById('questionFrame').src = `${questionPaperUrl}#toolbar=0`
}

async function loadExam() {
  setExamStatus('Loading exam details...', 'info')

  try {
    const response = await fetchWithSession(`${API_BASE_URL}/api/exam`)

    if (!response) {
      return
    }

    const data = await response.json()

    if (!response.ok || !data.success) {
      setExamStatus('Could not load the exam data.', 'error')
      return
    }

    renderExamHeader(data.student)
    startTimer(data.timerSeconds)
    await loadQuestionPaper(data.questionPaper)
    setExamStatus('Exam loaded successfully.', 'info')
  } catch (error) {
    console.error('Error loading exam:', error)
    setExamStatus('Failed to load the exam. Please verify the backend is running.', 'error')
  }
}

async function startCamera() {
  const video = document.getElementById('video')

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    setExamStatus('Camera access is not supported in this environment.', 'error')
    return
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: false
    })

    video.srcObject = stream
    setExamStatus('Camera connected. Good luck!', 'info')
  } catch (error) {
    console.error('Camera error:', error)
    setExamStatus('Please allow camera permission before starting the exam.', 'error')
  }
}

function goBackToDashboard() {
  window.location = 'dashboard.html'
}

document.addEventListener('contextmenu', event => event.preventDefault())
document.addEventListener('copy', event => event.preventDefault())
document.addEventListener('keydown', event => {
  if (event.ctrlKey && event.key.toLowerCase() === 'p') {
    event.preventDefault()
    setExamStatus('Printing is disabled during the exam.', 'error')
  }
})

window.addEventListener('beforeunload', () => {
  if (questionPaperUrl) {
    URL.revokeObjectURL(questionPaperUrl)
  }
})

window.addEventListener('load', async () => {
  if (window.electronAPI?.startFullscreen) {
    window.electronAPI.startFullscreen()
  }

  await loadExam()
  await startCamera()
})
