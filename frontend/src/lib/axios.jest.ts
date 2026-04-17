/**
 * Cliente HTTP mínimo para Jest (Node não interpreta import.meta como no Vite).
 * O bundle de produção continua a usar `axios.ts`.
 */
import axios from 'axios'

export const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: { 'Content-Type': 'application/json' },
})
