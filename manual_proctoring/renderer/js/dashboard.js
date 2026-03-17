const API_BASE_URL = 'http://localhost:5000'

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

function setStatus(message, type = 'info') {
  const status = document.getElementById('dashboardMessage')

  if (!status) {
    return
  }

  status.hidden = !message
  status.className = `status-message ${type}`
  status.innerText = message || ''
}

async function fetchWithSession(url, options = {}) {
  const session = getStoredSession()

  if (!session || !session.token) {
    redirectToLogin('Please sign in to continue.')
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

async function loadDashboard() {
  setStatus('Loading your exam details...', 'info')

  try {
    const response = await fetchWithSession(`${API_BASE_URL}/api/student`)

    if (!response) {
      return
    }

    const data = await response.json()

    if (!response.ok || !data.student) {
      setStatus('Could not load student details.', 'error')
      return
    }

    document.getElementById('studentName').innerText = data.student.name
    document.getElementById('studentEmail').innerText = data.student.email
    document.getElementById('examName').innerText = data.student.exam
    setStatus('You are ready to start the exam.', 'info')
  } catch (error) {
    setStatus('Could not reach the backend. Make sure the server is running.', 'error')
  }
}

function startExam() {
  setStatus('Opening exam...', 'info')
  window.location = 'exam.html'
}

async function logout() {
  const logoutButton = document.getElementById('logoutButton')

  if (logoutButton) {
    logoutButton.disabled = true
  }

  try {
    const response = await fetchWithSession(`${API_BASE_URL}/api/logout`, {
      method: 'POST'
    })

    if (response) {
      await response.json().catch(() => null)
    }
  } finally {
    clearSession()
    redirectToLogin('You have been logged out.')
  }
}

window.addEventListener('load', () => {
  loadDashboard()
})
