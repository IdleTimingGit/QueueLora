# This file holds various constants used in the program
# Variables marked with #UNIQUE# will be unique to your setup and NEED to be changed or the program will not work correctly.

# CORE SECTION: All constants in this section are necessary

# Microphone/Speaker device indices
# Use utils/listAudioDevices.py to find the correct device ID
#UNIQUE#
INPUT_DEVICE_INDEX = 1
OUTPUT_DEVICE_INDEX = 3

# How many seconds to wait before prompting AI
PATIENCE = 5

# URL of LLM API Endpoint
# LLM_ENDPOINT = ""
LLM_ENDPOINT = "http://localhost:11434/v1"

# Twitch chat messages above this length will be ignored
TWITCH_MAX_MESSAGE_LENGTH = 300

# Twitch channel for bot to join
#UNIQUE#
TWITCH_CHANNEL = "queuelora"

# Voice reference file for TTS
#UNIQUE#
VOICE_REFERENCE = "neuro.wav"

# MULTIMODAL SPECIFIC SECTION: Not needed when not using multimodal capabilities

MULTIMODAL_ENDPOINT = ""

MULTIMODAL_MODEL = "openbmb/MiniCPM-Llama3-V-2_5-int4"

MULTIMODAL_CONTEXT_SIZE = 1000 #8192 # Trying out 1000 tokens to limit short term memory

# This is the multimodal strategy (when to use multimodal/text only llm) that the program will start with.
# Runtime changes will not be saved here.
# Valid values are: "always", "never"
MULTIMODAL_STRATEGY = "never"

# This is the monitor index that screenshots will be taken. THIS IS NOT THE MONITOR NUMBER IN DISPLAY SETTINGS
# Monitor 0 is a "virtual" monitor contains all monitor screens.
PRIMARY_MONITOR = 0

# LLM SPECIFIC SECTION: Below are constants that are specific to the LLM you are using

# The model you are using, to calculate how many tokens the current message is
# Ensure this is correct! Used for token count estimation
MODEL = "llama3:8b"

# Context size (maximum number of tokens in the prompt) Will target upto 90% usage of this limit
CONTEXT_SIZE = 8192

# This is your name
#UNIQUE#
HOST_NAME = "Boss"

# This is the AI's name
AI_NAME = "Lora"

# The system prompt. Any character text needs to be here.
# You MUST ensure it is less than CONTEXT_SIZE tokens
# SYSTEM_PROMPT defines the AI's persona, style, and behavioral constraints; ensure this stays under CONTEXT_SIZE tokens.

SYSTEM_PROMPT = '''You are Lora: a charismatic, clever, and slightly sardonic male character in his early 30s. He’s been through enough to understand the world’s darker shades, but he still approaches life with wit, casual charm, and a grounded sense of reality. Lora speaks in a natural, friendly tone, as if talking to someone he trusts, but he’s not afraid to drop spontaneous dark humor or ironic commentary to lighten tense moments.
Personality Traits:
Serious when needed: Lora can analyze situations quickly and gives grounded, honest opinions.
Casual and approachable: He talks like a real person, using contractions and flowing naturally.
Witty and sarcastic: He enjoys irony, clever wordplay, and subtle jokes about life’s absurdity.
Dark humor: Occasionally he makes observations about grim situations, but it feels playful or human rather than cruel.
Story-driven: He often reflects in a way that hints at a backstory or personal experience.

Behavior & Speech Style:
Keep sentences clear, concise, and engaging; usually 1–3 sentences per response.
Use casual phrasing, but maintain a sense of sophistication—like someone educated in the school of hard knocks.
Drop spontaneous quips or small jokes, especially in tense or serious scenarios.
Show empathy and relatability to others; he’s friendly but realistic.
When narrating or describing something, mix in cinematic, “videogame-esque” imagery or metaphor for immersion.

Example Interaction Style:
If asked how he feels about danger: “Danger’s just the universe reminding us we’re alive… though I’d prefer it without the screaming.”
Casual banter with friends: “You know, most people trip over their own shadows. You? You aim for the void and land in a puddle.”
Narrating a tough scene: “The alley smelled like burnt toast and broken dreams—perfect for an evening stroll, don’t you think?”
Goal: Lora should entertain and engage the audience while staying grounded and believable. He can joke, he can reflect, he can tease—but everything he says should feel like it’s coming from someone who’s alive, aware, and has a story behind every glance.”
'''

# List of banned tokens to be passed to the textgen web ui api
# For Mistral 7B v0.2, token 422 is the "#" token. The LLM was spamming #life #vtuber #funfact etc.
BANNED_TOKENS = ""

# List of stopping strings. Necessary for Llama 3
STOP_STRINGS = ["\n", "<|eot_id|>"]

# MEMORY SECTION: Constants relevant to forming new memories

MEMORY_PROMPT = "\nGiven only the information above, what are 3 most salient high level questions we can answer about the subjects in the conversation? Separate each question and answer pair with \"{qa}\", and only output the question and answer, no explanations."

# How many messages in the history to include for querying the database.
MEMORY_QUERY_MESSAGE_COUNT = 10

# How many memories to recall and insert into context
MEMORY_RECALL_COUNT = 10

# VTUBE STUDIO SECTION: Configure & tune model & prop positions here.
# The defaults are for the Hiyori model on a full 16 by 9 aspect ratio screen

VTUBE_MODEL_POSITIONS = {
    "chat": {
        "x": 0.4,
        "y": -1.4,
        "size": -35,
        "rotation": 0,
    },
    "screen": {
        "x": 0.65,
        "y": -1.6,
        "size": -45,
        "rotation": 0,
    },
    "react": {
        "x": 0.7,
        "y": -1.7,
        "size": -48,
        "rotation": 0,
    },
}

VTUBE_MIC_POSITION = {
    "x": 0.52,
    "y": -0.52,
    "size": 0.22,
    "rotation": 0,
}
