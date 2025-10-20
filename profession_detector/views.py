# profession_detector/views.py
from django.shortcuts import render
from .services import suggest_professions

def profession_detector_view(request):
    context = {
        'suggestions': [],
        'submitted_text': '',
        'aviso_palavrao': None
    }
    
    if request.method == 'POST':
        hobbies_text = request.POST.get('hobbies', '')
        context['submitted_text'] = hobbies_text
        
        if hobbies_text:
            # A função agora retorna uma tupla (sugestões, aviso)
            suggestions, aviso_palavrao = suggest_professions(hobbies_text)
            
            context['suggestions'] = suggestions
            context['aviso_palavrao'] = aviso_palavrao

    return render(request, 'profession_detector/detector.html', context)