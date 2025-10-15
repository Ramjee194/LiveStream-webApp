import axios from "axios";

const API_BASE = "http://127.0.0.1:5000/api";

export const getOverlays = async () => {
  return axios.get(`${API_BASE}/overlays/`);
};

export const createOverlay = async (data) => {
  return axios.post(`${API_BASE}/overlays/`, data);
};

export const updateOverlay = async (name, data) => {
  return axios.put(`${API_BASE}/overlays/${name}`, data);
};

export const deleteOverlay = async (name) => {
  return axios.delete(`${API_BASE}/overlays/${name}`);
};

export const startStream = async (rtspUrl) => {
  return axios.post(`${API_BASE}/start-stream`, { rtsp_url: rtspUrl });
};
