const TELEGRAM_API_URL = `https://api.telegram.org/bot7911388028:AAHgr0DOiTYFua3y6dGRBnsoNOxU0soMPmU`;
const GEMINI_API_URL =
	'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=AIzaSyBDCeQQBj1FjM0KgD3ZRxYfvkPIxkDv3Vg';

async function handleUpdate(request) {
	console.log('Received update:', JSON.stringify(request));
	const { message } = await request.json();

	if (message && message.text) {
		if (message.text.startsWith('/start')) {
			// Handle the /start command
			const startMessage = `
Welcome to the AI Bot! 🎉
You can ask me anything by typing:

/ai YOUR_QUESTION

For example:
/ai What's the weather like today?
      `;
			await sendMessage(message.chat.id, startMessage);
			return new Response('OK', { status: 200 });
		}

		if (message.text.startsWith('/ai')) {
			const question = message.text.replace('/ai', '').trim();
			if (!question) {
				await sendMessage(message.chat.id, 'Please ask a question after /ai');
				return new Response('OK', { status: 200 });
			}
			const geminiResponse = await callGeminiApi(question);
			await sendMessage(message.chat.id, geminiResponse);
			return new Response('OK', { status: 200 });
		}
	}

	return new Response('OK', { status: 200 });
}

async function callGeminiApi(question) {
	const response = await fetch(GEMINI_API_URL, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({
			contents: [
				{
					parts: [{ text: question }],
				},
			],
		}),
	});
	const data = await response.json();
	return data.candidates[0].content.parts[0].text.trim() || "I couldn't find an answer.";
}

async function sendMessage(chatId, text) {
	await fetch(`${TELEGRAM_API_URL}/sendMessage`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ chat_id: chatId, text }),
	});
}

export default {
	async fetch(request) {
		if (request.method === 'POST') {
			return handleUpdate(request);
		}
		return new Response('Hello from Telegram Bot Worker!');
	},
};
