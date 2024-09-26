const TELEGRAM_API_URL = `https://api.telegram.org/bot7911388028:AAHgr0DOiTYFua3y6dGRBnsoNOxU0soMPmU`;
const GEMINI_API_URL =
	'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=AIzaSyBDCeQQBj1FjM0KgD3ZRxYfvkPIxkDv3Vg';
const CHANNEL_USERNAME = '@aasoft_ir';
const WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather';
const WEATHER_API_KEY = 'a060f8b99ad5c0185982cdfaddad548a';

// Function to handle incoming updates (messages, commands, etc.)
async function handleUpdate(request) {
	console.log('Received update:', JSON.stringify(request));
	const { message } = await request.json();

	// Ensure we have a message with text
	if (message && message.text) {
		const chatType = message.chat.type;
		const isPrivateChat = chatType === 'private';
		const isGroupChat = chatType === 'group' || chatType === 'supergroup'; // Handle group and supergroup

		// Check if the chat is private and verify the user is in the channel
		if (isPrivateChat) {
			const isMember = await isChannelMember(message.from.id);
			if (!isMember) {
				await sendMessage(message.chat.id, `Please join ${CHANNEL_USERNAME} to use this bot.`);
				return new Response('OK', { status: 200 });
			}
		}

		const command = message.text.split(' ')[0].toLowerCase(); // Get command (e.g., /start)
		const args = message.text.split(' ').slice(1).join(' '); // Get arguments after command

		// Handle commands based on input
		switch (command) {
			case '/start':
				await handleStart(message, chatType);
				break;
			case '/ai':
				await handleAI(message, args);
				break;
			case '/weather':
				await handleWeather(message, args);
				break;
			case '/poll':
				if (isGroupChat) {
					await handlePoll(message, args);
				} else {
					await sendMessage(message.chat.id, 'Polls can only be created in groups.');
				}
				break;
			case '/joke':
				await handleJoke(message);
				break;
			default:
				if (isPrivateChat) {
					await sendMessage(message.chat.id, 'Unknown command. Type /start for help.');
				}
		}
	}

	return new Response('OK', { status: 200 });
}

// Handle /start command
async function handleStart(message, chatType) {
	const startMessage =
		chatType === 'private'
			? `
Welcome to the Enhanced AI Bot! 🚀

Available commands:
/ai [question] - Ask the AI anything
/weather [city] - Get current weather
/poll [question] - Create a poll (in groups)
/joke - Get a random joke

Enjoy exploring! 😊
  `
			: `
Hello! I'm an AI bot that can help with various tasks. Here are some commands you can use in this ${chatType}:
/ai [question] - Ask the AI anything
/weather [city] - Get current weather
/poll [question] - Create a poll
/joke - Get a random joke

Feel free to interact with me!
  `;
	await sendMessage(message.chat.id, startMessage);
}

// Handle /ai command to interact with Gemini API
async function handleAI(message, question) {
	if (!question) {
		await sendMessage(message.chat.id, 'Please ask a question after /ai');
		return;
	}
	const geminiResponse = await callGeminiApi(question);
	await sendMessage(message.chat.id, geminiResponse);
}

// Handle /weather command to fetch weather info
async function handleWeather(message, city) {
	if (!city) {
		await sendMessage(message.chat.id, 'Please provide a city name after /weather');
		return;
	}
	const weatherData = await getWeather(city);
	await sendMessage(message.chat.id, weatherData);
}

// Handle /poll command to create a poll in group chats
async function handlePoll(message, question) {
	if (!question) {
		await sendMessage(message.chat.id, 'Please provide a question for the poll after /poll');
		return;
	}
	await createPoll(message.chat.id, question);
}

// Handle /joke command to fetch a random joke
async function handleJoke(message) {
	const joke = await getRandomJoke();
	await sendMessage(message.chat.id, joke);
}

// Check if a user is a member of the specified channel
async function isChannelMember(userId) {
	const response = await fetch(`${TELEGRAM_API_URL}/getChatMember`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ chat_id: CHANNEL_USERNAME, user_id: userId }),
	});
	const data = await response.json();
	return data.ok && ['member', 'administrator', 'creator'].includes(data.result.status);
}

// Call Gemini API to generate a response for the AI command
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

// Fetch weather data from OpenWeather API
async function getWeather(city) {
	const response = await fetch(`${WEATHER_API_URL}?q=${city}&appid=${WEATHER_API_KEY}&units=metric`);
	const data = await response.json();
	if (data.cod === 200) {
		return `Weather in ${data.name}: ${data.weather[0].description}, Temperature: ${data.main.temp}°C`;
	} else {
		return "Couldn't fetch weather data. Please check the city name.";
	}
}

// Create a poll in group chats
async function createPoll(chatId, question) {
	await fetch(`${TELEGRAM_API_URL}/sendPoll`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({
			chat_id: chatId,
			question: question,
			options: JSON.stringify(['Yes', 'No', 'Maybe']),
			is_anonymous: false,
		}),
	});
}

// Fetch a random joke from an external API
async function getRandomJoke() {
	const response = await fetch('https://official-joke-api.appspot.com/random_joke');
	const data = await response.json();
	return `${data.setup}\n\n${data.punchline}`;
}

// Send a message to a user or chat
async function sendMessage(chatId, text) {
	await fetch(`${TELEGRAM_API_URL}/sendMessage`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ chat_id: chatId, text }),
	});
}

// Main function to handle incoming requests
export default {
	async fetch(request) {
		if (request.method === 'POST') {
			return handleUpdate(request);
		}
		return new Response('Hello from Enhanced Telegram Bot Worker!');
	},
};
