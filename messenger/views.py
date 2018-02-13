import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from brain.planner import response_planner
from brain.planner import sentence_planner
from brain.conjugator import conjugator
from brain import generator
from brain import memory

# Create your views here.
@ensure_csrf_cookie
def index(request):
    context = {}
    #plan = sentence_planner.plan_from_memory("characters", "Piglet", key="species", subject="")
    #print(plan)
    #print(generator.generate_simple_sentence(plan['params'], plan['modifiers']))
    #print(conjugator.conjugate("jump over", number=conjugator.PLURAL, person=conjugator.THIRD_PERSON, tense=conjugator.PRESENT_TENSE))
    #print(interpreter.stanford_pos("King of Germans"))
    #print("final: ", sentence_planner.traverse_and_check("university", memory.CURRENT_CONTEXT, [],[]))
    #print(sentence_planner.plan_randomly_from_memory("Ateneo De Manila University", 2))
    return render(request, 'messenger/index.html', context)

def process_message(request):
#    user = None
#    if request.user.is_authenticated():
#        user = request.user.id
    message = json.loads(request.body.decode('utf-8'))['message']
    #print(message)
    #tagged = interpreter.tokenize_and_tag(message)
    #tagged = interpreter.stanford_pos(message)
    #keywords = interpreter.consolidate(interpreter.get_keywords(tagged))
    #sentence_structures = interpreter.get_sentence_structure(tagged)
    #output_message = "Input: '" + message + "'<br />" \
    #                + "Tagged: '" + json.dumps(tagged) + "'<br />" \
    #                + "Keywords: '" + json.dumps(keywords) + "'<br />" \
    #                + "Sentence Structures: '" + json.dumps(sentence_structures) + "'"
    #if len(keywords) == 0:
    #    plan = sentence_planner.describe_subject("")
    #else:
    #    print(keywords)
    #    choice = random.choice(keywords)
    #    print(choice)
    #    plan = sentence_planner.describe_subject(choice)
    #output_message = generate_trial.generate_simple_sentence(plan['params'], plan['modifiers'])
    #output_message = generate_trial.generate_simple_question(message, "What")
    output_message = response_planner.plan_response(message, {'num_sentences': 10, 'stutter':0.25})
    data = {'response': output_message}
    return JsonResponse(data)
