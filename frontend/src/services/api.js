import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

export async function fetchProjectEnergy() {
  const response = await api.get('/project-energy');
  return response.data;
}
