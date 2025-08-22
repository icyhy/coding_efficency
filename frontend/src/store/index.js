import { createStore } from 'vuex'
import auth from './modules/auth'
import analytics from './modules/analytics'
import repositories from './modules/repositories'

export default createStore({
  modules: {
    auth,
    analytics,
    repositories
  },
  strict: process.env.NODE_ENV !== 'production'
})