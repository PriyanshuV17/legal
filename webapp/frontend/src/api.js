import axios from "axios";

export const api = axios.create({
  baseURL: "http://127.0.0.1:8001/api"
});

export const rootApi = axios.create({
  baseURL: "http://127.0.0.1:8001"
});

export const apiPaths = {
  apiBase: "http://127.0.0.1:8001/api",
  rootBase: "http://127.0.0.1:8001"
};
