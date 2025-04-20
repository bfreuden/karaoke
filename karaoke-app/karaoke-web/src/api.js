import axios from 'axios';

const api = axios.create({baseURL:"/api"})
const files = axios.create({baseURL:"/static"})

export {
  api,
  files
}
