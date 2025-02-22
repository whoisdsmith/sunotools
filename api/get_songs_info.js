// get_songs_info.js
const axios = require('axios')
const fs = require('fs')

async function getSongInformation() {
    try {
        const response = await axios.get('http://localhost:3000/api/get')
        // Assuming your suno-api is running on localhost: 3000

        if (response.status === 200) {
            const songData = response.data

            // Output to console(optional)
            console.log('Successfully fetched song information:')
            console.log(JSON.stringify(songData, null, 2))

            // Write to a JSON file
            fs.writeFileSync('songs_info.json',
                             JSON.stringify(songData, null, 2))
            console.log('Song information saved to songs_info.json')
        } else {
            console.error(
                'Failed to fetch song information. Status code:', response.status)
            console.error('Response data:', response.data)
        }
    } catch(error) {
        console.error('Error fetching song information:', error.message)
        if (error.response) {
            console.error('Response status:', error.response.status)
            console.error('Response data:', error.response.data)
        }
    }
}

getSongInformation()
