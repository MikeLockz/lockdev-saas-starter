import axios from "axios";

export const api = axios.create({
	baseURL: "/api/v1",
	headers: {
		"Content-Type": "application/json",
	},
});

// TODO: specific typed wrappers can be added here once the schema is populated.
