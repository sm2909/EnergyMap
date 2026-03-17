import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8080/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

export async function fetchProjectEnergy() {
  const response = await api.get('/energy', {
    params: {
      project: "black",
    }
  });
  return response.data;
}
