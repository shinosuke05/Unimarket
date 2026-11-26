async function checkBackend() {
    try {
        const data = await apiRequest("/api/test");

        console.log(data.message);

    } catch (error) {
        console.error("Không thể kết nối Backend");
    }
}

checkBackend();