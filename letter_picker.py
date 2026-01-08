import random
from flask import Blueprint, render_template, session, jsonify

letter_picker_bp = Blueprint('letter_picker', __name__)

@letter_picker_bp.route('/letter_picker')
def letter_picker():
    """Main page for letter picker game"""
    # Initialize session variables if not present
    if 'used_letters' not in session:
        session['used_letters'] = []
    if 'current_letter' not in session:
        session['current_letter'] = ''
    
    return render_template('letter_picker.html', 
                         current_letter=session['current_letter'],
                         used_letters=', '.join(session['used_letters']))

@letter_picker_bp.route('/pick_letter', methods=['POST'])
def pick_letter():
    """API endpoint to pick a random letter"""
    # Initialize session if needed
    if 'used_letters' not in session:
        session['used_letters'] = []
    
    # Move current letter to used letters if it exists
    if 'current_letter' in session and session['current_letter']:
        if session['current_letter'] not in session['used_letters']:
            session['used_letters'].append(session['current_letter'])
    
    # Get all letters A-Z
    all_letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    
    # Filter out already used letters
    available_letters = [letter for letter in all_letters if letter not in session['used_letters']]
    
    # If no letters available, reset the game
    if not available_letters:
        session['used_letters'] = []
        available_letters = all_letters
    
    # Pick a random letter from available letters
    new_letter = random.choice(available_letters)
    
    # Set new current letter
    session['current_letter'] = new_letter
    session.modified = True
    
    return jsonify({
        'letter': new_letter,
        'used_letters': ', '.join(session['used_letters'])
    })

@letter_picker_bp.route('/reset_game', methods=['POST'])
def reset_game():
    """Reset the game state"""
    session['used_letters'] = []
    session['current_letter'] = ''
    session.modified = True
    
    return jsonify({
        'status': 'reset',
        'letter': '',
        'used_letters': ''
    })
