This project has the main goal of building an app that I can use myself, specifically when cooking, running or driving, as a way to rehearse trivia questions. What I want is
- an automatic queue of randomized questions
- read out loud
- with some time in between so I can think of the answer
- then getting the answer read out loud

Key features are:
- the randomization (else I will remember the sequence of answers)
- the automatic queue (else I have to manipulate my device while driving)

Way of working:  
I built the application as a "vibe coding" experiment, following instructions by ChatGPT. I have a fair understanding of the end result but I have a hard time debugging or improving.

Structure:
- The source files are csv files per category containing a number of questions and answers with "vraag,antwoord" as the key value pair.
- The main program is (currently) quiz_spoken_one_audio.py
- Two uxiliary files are config.toml and requirements.txt
- I have moved a couple of reusable functions to utils.py
- there are some other files with dead ends or attempts to have a different approach to the goal (getting questions out of wikipedia, and getting a different voice)

Problems with the current functionality:
- the main complaint I get from users is about the voice; it's the standard female "dutch dutch" voice in Google TTS. 
Voices in "dutch belgian" exist but require an account, or are not generated real time, or both. I need to make the step to an API key (with Amazon Polly e.g.) but that will need to be secured. Anything that is payable I'm holding off for now, not out of frugality but fear of exploitation. , ofwel is het asynchroon (niet real-time). Even better would be to have my own voice encoded for reuse. This is possible with ElevenLabs but a project in its own right.
- it might be better to have the questions transcribed once, store them in a db and then only do the random selection
- my first implementation was a queue of transcribed questions, but iOS and Android are protected against unpredictable on the fly audio, so I had to resolve to the merge operation
- the questions are not of the same quality: some are simply years and names, others have more context

Ideas for functional improvements:

- Answer the question vocally and have speech recognition into validation of the answer
- Tailor the queue or the next iteration to the questions which were not answered correctly
- Expose the app to a bigger audience, e.g. in an appstore
- More categories and more questions per category. This is hard to maintain. I have experimented with a Wikipedia API but to no avail
- Tap into OpenAI for questions
