import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')
  const nickname = ref(localStorage.getItem('nickname') || '')
  const userId = ref(Number(localStorage.getItem('userId')) || 0)

  function setLogin(data) {
    token.value = data.token
    username.value = data.username
    nickname.value = data.nickname
    userId.value = data.user_id
    localStorage.setItem('token', data.token)
    localStorage.setItem('username', data.username)
    localStorage.setItem('nickname', data.nickname)
    localStorage.setItem('userId', data.user_id)
  }

  function clearLogin() {
    token.value = ''
    username.value = ''
    nickname.value = ''
    userId.value = 0
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('nickname')
    localStorage.removeItem('userId')
  }

  const isLoggedIn = () => !!token.value

  return { token, username, nickname, userId, setLogin, clearLogin, isLoggedIn }
})
