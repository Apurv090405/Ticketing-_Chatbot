import tracemalloc
tracemalloc.start()
from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from pymongo import MongoClient
from chatbot import TicketingChatbot
import uuid
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# MongoDB setup
client = MongoClient("localhost", 27017)
db = client["Ticketing_Platform"]
customers_collection = db["Customers"]
tickets_collection = db["tickets"]

# Initialize chatbot
try:
    chatbot = TicketingChatbot()
    logger.info("Chatbot initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize chatbot: {e}")
    raise

# HTML template with improved UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LaptopS</title>
    <link href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-color: #3b82f6;
            --secondary-color: #60a5fa;
            --accent-color: #06b6d4;
            --text-color: #1e293b;
            --bg-color: #f8fafc;
            --sidebar-bg: rgba(255, 255, 255, 0.95);
            --message-bg-user: #3b82f6;
            --message-bg-bot: rgba(255, 255, 255, 0.9);
            --border-color: rgba(209, 213, 219, 0.6);
            --glass-bg: rgba(255, 255, 255, 0.1);
            --glass-border: rgba(255, 255, 255, 0.2);
            --tech-blue: #0ea5e9;
            --tech-cyan: #06b6d4;
            --tech-purple: #8b5cf6;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 25%, #e0f2fe 50%, #f8fafc 100%);
            color: var(--text-color);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }

        /* ADVANCED ANIMATED BACKGROUNDS */
        
        /* Floating Tech Particles */
        .tech-particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -10;
            overflow: hidden;
        }

        .particle {
            position: absolute;
            font-size: 20px;
            color: rgba(59, 130, 246, 0.3);
            animation: float 15s infinite linear;
        }

        .particle:nth-child(1) { left: 10%; animation-delay: 0s; font-size: 24px; }
        .particle:nth-child(2) { left: 20%; animation-delay: -2s; font-size: 18px; }
        .particle:nth-child(3) { left: 30%; animation-delay: -4s; font-size: 22px; }
        .particle:nth-child(4) { left: 40%; animation-delay: -6s; font-size: 16px; }
        .particle:nth-child(5) { left: 50%; animation-delay: -8s; font-size: 20px; }
        .particle:nth-child(6) { left: 60%; animation-delay: -10s; font-size: 26px; }
        .particle:nth-child(7) { left: 70%; animation-delay: -12s; font-size: 18px; }
        .particle:nth-child(8) { left: 80%; animation-delay: -14s; font-size: 24px; }
        .particle:nth-child(9) { left: 90%; animation-delay: -16s; font-size: 20px; }
        .particle:nth-child(10) { left: 5%; animation-delay: -18s; font-size: 22px; }

        @keyframes float {
            0% { 
                transform: translateY(100vh) rotate(0deg) scale(0.8);
                opacity: 0;
            }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { 
                transform: translateY(-20vh) rotate(360deg) scale(1.2);
                opacity: 0;
            }
        }

        /* Circuit Board Pattern */
        .circuit-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.1) 1px, transparent 1px),
                radial-gradient(circle at 80% 20%, rgba(6, 182, 212, 0.1) 1px, transparent 1px),
                radial-gradient(circle at 20% 80%, rgba(139, 92, 246, 0.1) 1px, transparent 1px),
                radial-gradient(circle at 80% 80%, rgba(59, 130, 246, 0.1) 1px, transparent 1px);
            background-size: 100px 100px, 120px 120px, 80px 80px, 90px 90px;
            animation: circuitMove 20s linear infinite;
            z-index: -9;
            opacity: 0.6;
        }

        @keyframes circuitMove {
            0% { background-position: 0px 0px, 0px 0px, 0px 0px, 0px 0px; }
            100% { background-position: 100px 100px, -120px 120px, 80px -80px, -90px 90px; }
        }

        /* Gradient Waves */
        .wave-layer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 200%;
            height: 300px;
            z-index: -8;
        }

        .wave1 {
            background: linear-gradient(45deg, 
                transparent 0%,
                rgba(59, 130, 246, 0.1) 25%,
                rgba(6, 182, 212, 0.15) 50%,
                rgba(59, 130, 246, 0.1) 75%,
                transparent 100%);
            animation: wave1Animation 18s ease-in-out infinite;
            border-radius: 50% 50% 0 0;
        }

        .wave2 {
            background: linear-gradient(-45deg, 
                transparent 0%,
                rgba(139, 92, 246, 0.08) 20%,
                rgba(59, 130, 246, 0.12) 50%,
                rgba(6, 182, 212, 0.08) 80%,
                transparent 100%);
            animation: wave2Animation 25s ease-in-out infinite reverse;
            border-radius: 60% 40% 0 0;
            height: 250px;
        }

        .wave3 {
            background: linear-gradient(90deg, 
                transparent 0%,
                rgba(6, 182, 212, 0.06) 30%,
                rgba(59, 130, 246, 0.1) 60%,
                rgba(139, 92, 246, 0.06) 90%,
                transparent 100%);
            animation: wave3Animation 30s ease-in-out infinite;
            border-radius: 70% 30% 0 0;
            height: 200px;
        }

        @keyframes wave1Animation {
            0%, 100% { 
                transform: translateX(-25%) rotate(0deg) scaleY(0.8);
                opacity: 0.7;
            }
            50% { 
                transform: translateX(0%) rotate(2deg) scaleY(1.2);
                opacity: 1;
            }
        }

        @keyframes wave2Animation {
            0%, 100% { 
                transform: translateX(15%) rotate(-1deg) scaleY(0.6);
                opacity: 0.5;
            }
            50% { 
                transform: translateX(-10%) rotate(1deg) scaleY(1);
                opacity: 0.8;
            }
        }

        @keyframes wave3Animation {
            0%, 100% { 
                transform: translateX(-30%) rotate(1deg) scaleY(0.4);
                opacity: 0.3;
            }
            50% { 
                transform: translateX(5%) rotate(-1deg) scaleY(0.8);
                opacity: 0.6;
            }
        }

        /* Binary Rain Effect */
        .binary-rain {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -7;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            color: rgba(59, 130, 246, 0.2);
            overflow: hidden;
        }

        .binary-column {
            position: absolute;
            top: -100%;
            white-space: nowrap;
            animation: binaryFall 12s linear infinite;
        }

        .binary-column:nth-child(1) { left: 5%; animation-delay: 0s; }
        .binary-column:nth-child(2) { left: 15%; animation-delay: -2s; }
        .binary-column:nth-child(3) { left: 25%; animation-delay: -4s; }
        .binary-column:nth-child(4) { left: 35%; animation-delay: -6s; }
        .binary-column:nth-child(5) { left: 45%; animation-delay: -8s; }
        .binary-column:nth-child(6) { left: 55%; animation-delay: -10s; }
        .binary-column:nth-child(7) { left: 65%; animation-delay: -1s; }
        .binary-column:nth-child(8) { left: 75%; animation-delay: -3s; }
        .binary-column:nth-child(9) { left: 85%; animation-delay: -5s; }
        .binary-column:nth-child(10) { left: 95%; animation-delay: -7s; }

        @keyframes binaryFall {
            0% { transform: translateY(-100vh); opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { transform: translateY(100vh); opacity: 0; }
        }

        /* Floating Geometric Shapes */
        .geometric-shapes {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -6;
            overflow: hidden;
        }

        .shape {
            position: absolute;
            border: 2px solid rgba(59, 130, 246, 0.2);
            animation: shapeFloat 20s infinite ease-in-out;
        }

        .shape.circle {
            border-radius: 50%;
            width: 60px;
            height: 60px;
        }

        .shape.square {
            width: 50px;
            height: 50px;
            transform: rotate(45deg);
        }

        .shape.triangle {
            width: 0;
            height: 0;
            border-left: 25px solid transparent;
            border-right: 25px solid transparent;
            border-bottom: 50px solid rgba(59, 130, 246, 0.2);
            border-top: none;
        }

        .shape:nth-child(1) { top: 10%; left: 10%; animation-delay: 0s; }
        .shape:nth-child(2) { top: 20%; left: 80%; animation-delay: -3s; }
        .shape:nth-child(3) { top: 60%; left: 15%; animation-delay: -6s; }
        .shape:nth-child(4) { top: 80%; left: 70%; animation-delay: -9s; }
        .shape:nth-child(5) { top: 40%; left: 90%; animation-delay: -12s; }

        @keyframes shapeFloat {
            0%, 100% { transform: translateY(0px) rotate(0deg) scale(1); }
            25% { transform: translateY(-20px) rotate(90deg) scale(1.1); }
            50% { transform: translateY(0px) rotate(180deg) scale(0.9); }
            75% { transform: translateY(-15px) rotate(270deg) scale(1.05); }
        }

        /* Data Stream Effect */
        .data-stream {
            position: fixed;
            top: 0;
            right: -10px;
            width: 200px;
            height: 100%;
            background: linear-gradient(
                to bottom,
                transparent 0%,
                rgba(59, 130, 246, 0.1) 20%,
                rgba(6, 182, 212, 0.15) 50%,
                rgba(59, 130, 246, 0.1) 80%,
                transparent 100%
            );
            animation: dataFlow 8s linear infinite;
            z-index: -5;
            transform: skewX(-5deg);
        }

        @keyframes dataFlow {
            0% { transform: translateY(-100%) skewX(-5deg); opacity: 0; }
            20% { opacity: 1; }
            80% { opacity: 1; }
            100% { transform: translateY(100%) skewX(-5deg); opacity: 0; }
        }

        /* Pulsing Tech Grid */
        .tech-grid {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(rgba(59, 130, 246, 0.1) 1px, transparent 1px),
                linear-gradient(90deg, rgba(59, 130, 246, 0.1) 1px, transparent 1px);
            background-size: 50px 50px;
            animation: gridPulse 4s ease-in-out infinite;
            z-index: -4;
        }

        @keyframes gridPulse {
            0%, 100% { opacity: 0.3; transform: scale(1); }
            50% { opacity: 0.6; transform: scale(1.02); }
        }

        /* Main Container Styles (Unchanged Logic) */
        .main-container {
            display: flex;
            width: 100%;
            height: 100vh;
            max-width: 1400px;
            position: relative;
            z-index: 1;
        }

        .sidebar {
            width: 320px;
            background: var(--sidebar-bg);
            backdrop-filter: blur(20px);
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 24px;
            border-right: 1px solid var(--glass-border);
            box-shadow: 0 0 50px rgba(59, 130, 246, 0.1);
            position: relative;
            z-index: 10;
            border-radius: 0 20px 20px 0;
        }

        .sidebar::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, 
                rgba(255, 255, 255, 0.2) 0%, 
                rgba(255, 255, 255, 0.1) 100%);
            border-radius: 0 20px 20px 0;
            z-index: -1;
        }

        .sidebar h1 {
            font-size: 26px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color), var(--accent-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0;
            text-align: center;
            animation: titleGlow 3s ease-in-out infinite alternate;
        }

        @keyframes titleGlow {
            0% { filter: drop-shadow(0 0 5px rgba(59, 130, 246, 0.3)); }
            100% { filter: drop-shadow(0 0 15px rgba(59, 130, 246, 0.5)); }
        }

        .sidebar .user-info, .sidebar .instructions {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(15px);
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .sidebar .user-info:hover, .sidebar .instructions:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(59, 130, 246, 0.15);
        }

        .sidebar .user-info p {
            margin: 10px 0;
            font-size: 14px;
            color: var(--text-color);
            font-weight: 500;
        }

        .sidebar .user-info p strong {
            color: var(--primary-color);
        }

        .sidebar .instructions h3 {
            font-size: 18px;
            margin-bottom: 16px;
            color: var(--primary-color);
            font-weight: 600;
        }

        .sidebar .instructions ul {
            padding-left: 20px;
            font-size: 14px;
            color: var(--text-color);
            line-height: 1.6;
        }

        .sidebar .instructions li {
            margin-bottom: 8px;
            transition: color 0.3s ease;
        }

        .sidebar .instructions li:hover {
            color: var(--primary-color);
        }

        .sidebar .logout-btn {
            padding: 14px;
            border: none;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            border-radius: 12px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            text-align: center;
            text-decoration: none;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
            position: relative;
            overflow: hidden;
        }

        .sidebar .logout-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(59, 130, 246, 0.4);
        }

        .sidebar .logout-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s ease;
        }

        .sidebar .logout-btn:hover::before {
            left: 100%;
        }

        .container {
            flex: 1;
            display: flex;
            flex-direction: column;
            height: 100vh;
            position: relative;
        }

        .chat-container {
            background: rgba(255, 255, 255, 0.3);
            backdrop-filter: blur(0px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 20px 0 0 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            height: 100%;
            overflow: hidden;
            position: relative;
        }

        .chat-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, 
                rgba(255, 255, 255, 0.1) 0%, 
                rgba(255, 255, 255, 0.05) 50%, 
                rgba(255, 255, 255, 0.1) 100%);
            z-index: -1;
            border-radius: 20px 0 0 20px;
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 24px;
            background: transparent;
            scrollbar-width: thin;
            scrollbar-color: rgba(59, 130, 246, 0.3) transparent;
        }

        .chat-messages::-webkit-scrollbar {
            width: 6px;
        }

        .chat-messages::-webkit-scrollbar-track {
            background: transparent;
        }

        .chat-messages::-webkit-scrollbar-thumb {
            background: rgba(59, 130, 246, 0.3);
            border-radius: 3px;
        }

        .chat-message {
            display: flex;
            align-items: flex-start;
            margin: 20px 0;
            animation: messageSlide 0.5s ease-out;
        }

        @keyframes messageSlide {
            from { 
                opacity: 0; 
                transform: translateY(20px) scale(0.95); 
            }
            to { 
                opacity: 1; 
                transform: translateY(0) scale(1); 
            }
        }

        .chat-message .icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            flex-shrink: 0;
            margin: 6px 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            animation: iconPulse 2s ease-in-out infinite;
        }

        @keyframes iconPulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }

        .user-message {
            flex-direction: row-reverse;
        }

        .user-message .icon {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
        }

        .bot-message .icon {
            background: linear-gradient(135deg, var(--secondary-color), var(--accent-color));
            color: white;
        }

        .message-content {
            position: relative;
            max-width: 75%;
            padding: 16px 20px;
            border-radius: 16px;
            font-size: 15px;
            line-height: 1.6;
            word-break: break-word;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }

        .user-message .message-content {
            background: rgba(59, 130, 246, 0.6);
            color: white;
            margin-left: 12px;
            border-bottom-right-radius: 6px;
            box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
        }

        .bot-message .message-content {
            background: rgba(255, 255, 255, 0.6);
            color: var(--text-color);
            margin-right: 12px;
            border-bottom-left-radius: 6px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        .loading-animation {
            display: flex;
            gap: 6px;
            padding: 16px 20px;
            max-width: 75%;
            margin: 20px 0 20px 12px;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }

        .loading-animation .dot {
            width: 10px;
            height: 10px;
            background: var(--primary-color);
            border-radius: 50%;
            animation: dotBounce 1.4s infinite ease-in-out;
        }

        .loading-animation .dot:nth-child(2) {
            animation-delay: -0.32s;
        }

        .loading-animation .dot:nth-child(3) {
            animation-delay: -0.16s;
        }

        @keyframes dotBounce {
            0%, 80%, 100% { 
                transform: scale(0.8); 
                opacity: 0.5; 
                background: var(--primary-color);
            }
            40% { 
                transform: scale(1.2); 
                opacity: 1; 
                background: var(--accent-color);
            }
        }

        .input-container {
            display: flex;
            padding: 20px 24px;
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(15px);
            border-top: 1px solid rgba(255, 255, 255, 0.3);
            gap: 12px;
            align-items: center;
            border-radius: 0 0 0 20px;
        }

        input[type="text"] {
            flex: 1;
            padding: 14px 18px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 12px;
            font-size: 15px;
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            color: var(--text-color);
            transition: all 0.3s ease;
        }

        input[type="text"]::placeholder {
            color: #6b7280;
        }

        input[type="text"]:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            outline: none;
            background: rgba(255, 255, 255, 1);
            transform: scale(1.02);
        }

        button {
            padding: 14px 24px;
            border: none;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            border-radius: 12px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
            position: relative;
            overflow: hidden;
        }

        button:hover {
            transform: translateY(-2px) scale(1.05);
            box-shadow: 0 6px 25px rgba(59, 130, 246, 0.4);
        }

        button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s ease;
        }

        button:hover::before {
            left: 100%;
        }

        button:active {
            transform: translateY(0) scale(1.02);
        }

        /* LOGIN PAGE STYLES */
        body.login {
            background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 25%, #e0f2fe 50%, #f8fafc 100%);
        }

        .login-container {
            max-width: 420px;
            margin: auto;
            padding: 40px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(25px);
            border-radius: 24px;
            box-shadow: 0 25px 60px rgba(59, 130, 246, 0.15);
            text-align: center;
            z-index: 10;
            border: 1px solid rgba(255, 255, 255, 0.3);
            position: relative;
            animation: loginFloat 3s ease-in-out infinite alternate;
        }

        @keyframes loginFloat {
            0% { transform: translateY(0px) rotate(0deg); }
            100% { transform: translateY(-10px) rotate(0.5deg); }
        }

        .login-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, 
                rgba(255, 255, 255, 0.2) 0%, 
                rgba(255, 255, 255, 0.1) 50%,
                rgba(255, 255, 255, 0.2) 100%);
            border-radius: 24px;
            z-index: -1;
        }

        .login-container h2 {
            font-size: 28px;
            font-weight: 600;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color), var(--accent-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 32px;
            animation: titleShimmer 3s ease-in-out infinite;
        }

        @keyframes titleShimmer {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }

        .login-container input[type="text"] {
            width: 100%;
            margin-bottom: 20px;
        }

        .login-container button {
            width: 100%;
        }

        .error {
            color: #ef4444;
            font-size: 14px;
            margin-top: 16px;
            font-weight: 500;
            animation: errorShake 0.5s ease-in-out;
        }

        @keyframes errorShake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }

        /* RESPONSIVE DESIGN */
        @media (max-width: 900px) {
            .main-container {
                flex-direction: column;
            }

            .sidebar {
                width: 100%;
                border-right: none;
                border-bottom: 1px solid var(--glass-border);
                height: auto;
                border-radius: 20px 20px 0 0;
            }

            .sidebar::before {
                border-radius: 20px 20px 0 0;
            }

            .container {
                height: calc(100vh - 300px);
            }

            .chat-container {
                border-radius: 0 0 20px 20px;
            }

            .chat-container::before {
                border-radius: 0 0 20px 20px;
            }

            .input-container {
                border-radius: 0 0 20px 20px;
            }

            /* Adjust particle count for mobile */
            .particle:nth-child(n+6) {
                display: none;
            }

            .binary-column:nth-child(n+6) {
                display: none;
            }

            .shape:nth-child(n+4) {
                display: none;
            }
        }

        @media (max-width: 600px) {
            .chat-messages {
                padding: 16px;
            }

            .message-content {
                max-width: 85%;
                font-size: 14px;
                padding: 12px 16px;
            }

            .input-container {
                padding: 16px;
            }

            input[type="text"], button {
                font-size: 14px;
                padding: 12px;
            }

            .login-container {
                padding: 32px 24px;
                margin: 20px;
                border-radius: 20px;
            }

            .login-container::before {
                border-radius: 20px;
            }

            .sidebar {
                padding: 16px;
            }

            /* Further reduce animations on very small screens */
            .particle:nth-child(n+4) {
                display: none;
            }

            .binary-column:nth-child(n+4) {
                display: none;
            }

            .wave-layer {
                height: 150px;
            }

            .wave2 {
                height: 120px;
            }

            .wave3 {
                height: 100px;
            }
        }

        /* ADDITIONAL TECH ANIMATIONS */
        
        /* Floating Code Elements */
        .code-floating {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -3;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            color: rgba(59, 130, 246, 0.15);
            overflow: hidden;
        }

        .code-element {
            position: absolute;
            animation: codeFloat 25s linear infinite;
            opacity: 0;
        }

        .code-element:nth-child(1) { top: 10%; left: 5%; animation-delay: 0s; }
        .code-element:nth-child(2) { top: 30%; left: 15%; animation-delay: -5s; }
        .code-element:nth-child(3) { top: 50%; left: 25%; animation-delay: -10s; }
        .code-element:nth-child(4) { top: 70%; left: 35%; animation-delay: -15s; }
        .code-element:nth-child(5) { top: 20%; left: 75%; animation-delay: -20s; }
        .code-element:nth-child(6) { top: 60%; left: 85%; animation-delay: -3s; }

        @keyframes codeFloat {
            0% { 
                opacity: 0; 
                transform: translateY(0px) rotate(0deg); 
            }
            10% { 
                opacity: 1; 
            }
            90% { 
                opacity: 1; 
            }
            100% { 
                opacity: 0; 
                transform: translateY(-50px) rotate(360deg); 
            }
        }

        /* Glowing Orbs */
        .glowing-orbs {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -2;
            overflow: hidden;
        }

        .orb {
            position: absolute;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(59, 130, 246, 0.3) 0%, rgba(59, 130, 246, 0.1) 50%, transparent 100%);
            animation: orbMove 20s ease-in-out infinite;
        }

        .orb:nth-child(1) {
            width: 100px;
            height: 100px;
            top: 20%;
            left: 10%;
            animation-delay: 0s;
        }

        .orb:nth-child(2) {
            width: 150px;
            height: 150px;
            top: 60%;
            left: 70%;
            animation-delay: -7s;
        }

        .orb:nth-child(3) {
            width: 80px;
            height: 80px;
            top: 80%;
            left: 20%;
            animation-delay: -14s;
        }

        @keyframes orbMove {
            0%, 100% { 
                transform: translate(0px, 0px) scale(1);
                opacity: 0.3;
            }
            25% { 
                transform: translate(30px, -40px) scale(1.2);
                opacity: 0.6;
            }
            50% { 
                transform: translate(-20px, -20px) scale(0.8);
                opacity: 0.4;
            }
            75% { 
                transform: translate(40px, 30px) scale(1.1);
                opacity: 0.5;
            }
        }

        /* Network Connection Lines */
        .network-lines {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
            overflow: hidden;
        }

        .network-line {
            position: absolute;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.3), transparent);
            animation: lineMove 8s linear infinite;
        }

        .network-line:nth-child(1) {
            top: 25%;
            width: 200px;
            left: -200px;
            animation-delay: 0s;
        }

        .network-line:nth-child(2) {
            top: 50%;
            width: 150px;
            left: -150px;
            animation-delay: -2s;
        }

        .network-line:nth-child(3) {
            top: 75%;
            width: 180px;
            left: -180px;
            animation-delay: -4s;
        }

        @keyframes lineMove {
            0% { transform: translateX(0); opacity: 0; }
            20% { opacity: 1; }
            80% { opacity: 1; }
            100% { transform: translateX(calc(100vw + 200px)); opacity: 0; }
        }
    </style>
</head>
<body class="{% if not username %}login{% endif %}">
    <!-- ANIMATED BACKGROUND ELEMENTS -->
    
    <!-- Tech Particles -->
    <div class="tech-particles">
        <div class="particle"><i class="fas fa-laptop"></i></div>
        <div class="particle"><i class="fas fa-microchip"></i></div>
        <div class="particle"><i class="fas fa-cog"></i></div>
        <div class="particle"><i class="fas fa-wifi"></i></div>
        <div class="particle"><i class="fas fa-server"></i></div>
        <div class="particle"><i class="fas fa-code"></i></div>
        <div class="particle"><i class="fas fa-desktop"></i></div>
        <div class="particle"><i class="fas fa-mobile-alt"></i></div>
        <div class="particle"><i class="fas fa-database"></i></div>
        <div class="particle"><i class="fas fa-cloud"></i></div>
    </div>

    <!-- Circuit Board Background -->
    <div class="circuit-bg"></div>

    <!-- Gradient Wave Layers -->
    <div class="wave-layer wave1"></div>
    <div class="wave-layer wave2"></div>
    <div class="wave-layer wave3"></div>

    <!-- Binary Rain Effect -->
    <div class="binary-rain">
        <div class="binary-column">01001000 01100101 01101100 01110000<br>01000100 01100101 01110011 01101011<br>01010011 01110101 01110000 01110000<br>01001100 01100001 01110000 01110100</div>
        <div class="binary-column">01010100 01100101 01100011 01101000<br>01000001 01110011 01110011 01101001<br>01010011 01110100 01100001 01101110<br>01000011 01101000 01100001 01110100</div>
        <div class="binary-column">01001000 01100001 01110010 01100100<br>01010111 01100001 01110010 01100101<br>01010011 01101111 01100110 01110100<br>01010111 01100001 01110010 01100101</div>
        <div class="binary-column">01000011 01101111 01101101 01110000<br>01010101 01110100 01100101 01110010<br>01010011 01100011 01110010 01100101<br>01100101 01101110 01000110 01101001</div>
        <div class="binary-column">01001011 01100101 01111001 01100010<br>01101111 01100001 01110010 01100100<br>01001101 01101111 01110101 01110011<br>01100101 01010000 01100001 01100100</div>
        <div class="binary-column">01010010 01000001 01001101 01000011<br>01010000 01010101 01000111 01010000<br>01010101 01010011 01000100 01001000<br>01000100 01010011 01010011 01000100</div>
        <div class="binary-column">01001001 01001111 01010000 01101111<br>01110010 01110100 01010101 01010011<br>01000010 01001000 01000100 01001101<br>01001001 01001000 01000100 01001101</div>
        <div class="binary-column">01010111 01101001 01000110 01101001<br>01000010 01101100 01110101 01100101<br>01110100 01101111 01101111 01110100<br>01101000 01000101 01110100 01101000</div>
        <div class="binary-column">01001100 01100001 01110000 01110100<br>01101111 01110000 01000100 01100101<br>01110011 01101011 01110100 01101111<br>01110000 01010100 01100001 01100010</div>
        <div class="binary-column">01010000 01110010 01101111 01100011<br>01100101 01110011 01110011 01101111<br>01110010 01001101 01100101 01101101<br>01101111 01110010 01111001 01000011</div>
    </div>

    <!-- Floating Geometric Shapes -->
    <div class="geometric-shapes">
        <div class="shape circle"></div>
        <div class="shape square"></div>
        <div class="shape triangle"></div>
        <div class="shape circle"></div>
        <div class="shape square"></div>
    </div>

    <!-- Data Stream -->
    <div class="data-stream"></div>

    <!-- Tech Grid -->
    <div class="tech-grid"></div>

    <!-- Floating Code Elements -->
    <div class="code-floating">
        <div class="code-element">function checkLaptop() {<br>&nbsp;&nbsp;return status.ok;<br>}</div>
        <div class="code-element">if (issue.found) {<br>&nbsp;&nbsp;diagnose();<br>}</div>
        <div class="code-element">class Support {<br>&nbsp;&nbsp;resolve();<br>}</div>
        <div class="code-element">const help = new<br>TechSupport();</div>
        <div class="code-element">while (problem) {<br>&nbsp;&nbsp;solve();<br>}</div>
        <div class="code-element">async function<br>fixIssue() {}</div>
    </div>

    <!-- Glowing Orbs -->
    <div class="glowing-orbs">
        <div class="orb"></div>
        <div class="orb"></div>
        <div class="orb"></div>
    </div>

    <!-- Network Lines -->
    <div class="network-lines">
        <div class="network-line"></div>
        <div class="network-line"></div>
        <div class="network-line"></div>
    </div>

    <!-- MAIN CONTENT -->
    <div class="{% if username %}main-container{% else %}container{% endif %}">
        {% if username %}
        <div class="sidebar">
            <h1><i class="fas fa-laptop"></i> Laptop Support</h1>
            <div class="user-info">
                <p><strong><i class="fas fa-user"></i> Username:</strong> {{ username }}</p>
                <p><strong><i class="fas fa-envelope"></i> Email:</strong> {{ username }}@example.com</p>
            </div>
            <div class="instructions">
                <h3><i class="fas fa-question-circle"></i> How to Use</h3>
                <ul>
                    <li><i class="fas fa-search"></i> Ask about laptop issues</li>
                    <li><i class="fas fa-list"></i> Type "list devices" to see available devices</li>
                    <li><i class="fas fa-comment"></i> Describe your problem clearly for precise solutions</li>
                    <li><i class="fas fa-keyboard"></i> Use the input box below to send your queries</li>
                </ul>
            </div>
            <a href="/logout" class="logout-btn">
                <i class="fas fa-sign-out-alt"></i> Logout
            </a>
        </div>
        {% endif %}
        
        <div class="container">
            {% if not username %}
            <div class="login-container">
                <h2><i class="fas fa-laptop"></i> Welcome to LaptopS</h2>
                <form id="loginForm">
                    <input type="text" id="username" placeholder="Enter your username" required>
                    <button type="submit"><i class="fas fa-sign-in-alt"></i> Login</button>
                </form>
                <p id="error" class="error"></p>
            </div>
            <script>
                document.getElementById('loginForm').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const username = document.getElementById('username').value.trim();
                    if (!username) {
                        document.getElementById('error').textContent = 'Please enter a username';
                        return;
                    }
                    const response = await fetch('/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username })
                    });
                    const result = await response.json();
                    if (result.success) {
                        window.location.href = `/?username=${result.username}`;
                    } else {
                        document.getElementById('error').textContent = result.message;
                    }
                });
            </script>
            {% else %}
            <div class="chat-container">
                <div class="chat-messages" id="chatMessages"></div>
                <div class="input-container">
                    <input type="text" id="messageInput" placeholder="Ask about your laptop or list devices...">
                    <button onclick="sendMessage()"><i class="fas fa-paper-plane"></i> Send</button>
                </div>
            </div>
            <script>
                async function sendMessage() {
                    const messageInput = document.getElementById('messageInput');
                    const message = messageInput.value.trim();
                    if (!message) return;
                    
                    const chatMessages = document.getElementById('chatMessages');
                    const userMessage = document.createElement('div');
                    userMessage.className = 'chat-message user-message';
                    userMessage.innerHTML = `<div class="icon"><i class="fas fa-user"></i></div><div class="message-content">${message}</div>`;
                    chatMessages.appendChild(userMessage);
                    
                    const loadingMessage = document.createElement('div');
                    loadingMessage.className = 'chat-message bot-message';
                    loadingMessage.innerHTML = `
                        <div class="icon"><i class="fas fa-robot"></i></div>
                        <div class="loading-animation">
                            <div class="dot"></div>
                            <div class="dot"></div>
                            <div class="dot"></div>
                        </div>`;
                    chatMessages.appendChild(loadingMessage);
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                    
                    try {
                        const response = await fetch(`/chat?username={{ username }}`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ message })
                        });
                        const result = await response.json();
                        
                        chatMessages.removeChild(loadingMessage);
                        const botMessage = document.createElement('div');
                        botMessage.className = 'chat-message bot-message';
                        botMessage.innerHTML = `<div class="icon"><i class="fas fa-robot"></i></div><div class="message-content">${result.response}</div>`;
                        chatMessages.appendChild(botMessage);
                    } catch (error) {
                        chatMessages.removeChild(loadingMessage);
                        const errorMessage = document.createElement('div');
                        errorMessage.className = 'chat-message bot-message';
                        errorMessage.innerHTML = `<div class="icon"><i class="fas fa-exclamation-triangle"></i></div><div class="message-content">An error occurred. Please try again.</div>`;
                        chatMessages.appendChild(errorMessage);
                    }
                    
                    messageInput.value = '';
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }

                document.getElementById('messageInput').addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') sendMessage();
                });
            </script>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""
@app.route('/')
def index():
    username = request.args.get('username')
    if username and customers_collection.find_one({"username": username}):
        logger.info(f"User {username} accessed chat interface")
        return render_template_string(HTML_TEMPLATE, username=username)
    logger.info("No username provided, showing login page")
    return render_template_string(HTML_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        if not username:
            logger.warning("Login attempted with empty username")
            return jsonify({"success": False, "message": "Username is required"})
        username = username.strip()
        user = customers_collection.find_one({"username": username})
        if user:
            logger.info(f"User {username} logged in successfully")
            return jsonify({"success": True, "username": username, "message": f"Welcome back, {username}!"})
        new_username = f"user_{uuid.uuid4().hex[:8]}"
        customer_id = f"CUST{str(uuid.uuid4())[:6]}"
        customers_collection.insert_one({
            "username": new_username,
            "customer_id": customer_id,
            "name": username,
            "laptops": []
        })
        logger.info(f"Created new user with username {new_username}")
        return jsonify({"success": True, "username": new_username, "message": f"New user created! Your username is {new_username}."})
    except Exception as e:
        logger.error(f"Error during login: {e}")
        return jsonify({"success": False, "message": "An error occurred during login"})

@app.route('/logout')
def logout():
    logger.info("User logged out")
    return redirect(url_for('index'))

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message')
        username = request.args.get('username', 'unknown')
        if not message or not message.strip():
            logger.warning(f"Empty message from user {username}")
            return jsonify({"response": "Please enter a message"})
        message = message.strip()
        logger.info(f"Processing message from {username}: {message}")
        response = chatbot.handle_message(username, message)
        logger.info(f"Response to {username}: {response}")
        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        return jsonify({"response": "An error occurred. Please try again."})

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(debug=True)