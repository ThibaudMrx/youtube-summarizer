async function summarize() {
	// Grab the URL from the input field
	const url = document.getElementById('videoUrl').value.trim();
	const resultEl = document.getElementById('result');

	if (!url) {
		alert('Please enter a YouTube URL.');
		return;
	}

	// 1) Show a "Processing" text that animates dots
	let dotCount = 0;
	resultEl.textContent = 'Processing (this can take a few minutes) .';
	const dotInterval = setInterval(() => {
		dotCount = (dotCount + 1) % 4; // cycle through 0..3
		resultEl.textContent = 'Processing (this can take a few minutes) ' + '.'.repeat(dotCount);
	}, 500);

	try {
		// 2) Send POST request to /summarize endpoint
		const response = await fetch('/summarize', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ url: url }),
		});

		if (!response.ok) {
			// handle error
			const errorData = await response.json();
			throw new Error(errorData.detail || response.statusText);
		}

		// 3) Parse JSON, display summary
		const data = await response.json();
		resultEl.textContent = data.summary;
	} catch (error) {
		console.error(error);
		resultEl.textContent = 'Error: ' + error.message;
	} finally {
		// 4) Stop the "Processing" animation
		clearInterval(dotInterval);
	}
}
