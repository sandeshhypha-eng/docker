import axios from "axios";

// Use relative URL so it goes through the dev server which can proxy to the backend
const apiUrl = "/api/tasks";

console.log("Using API URL:", apiUrl);

export function getTasks() {
    return axios.get(apiUrl);
}

export function addTask(task) {
    return axios.post(apiUrl, task);
}

export function updateTask(id, task) {
    return axios.put(apiUrl + "/" + id, task);
}

export function deleteTask(id) {
    return axios.delete(apiUrl + "/" + id);
}
