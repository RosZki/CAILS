import json
import os

from ruamel.yaml import YAML
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from CAILS.settings import CONTEXT_DIR
from brain import logger
from brain import memory

from brain import dialogue_manager

# Create your views here.
@ensure_csrf_cookie
def index(request):
    context = {'introduction':dialogue_manager.introduce()}
    #plan = sentence_planner.plan_from_memory("characters", "Piglet", key="species", subject="")
    #print(plan)
    #print(generator.generate_simple_sentence(plan['params'], plan['modifiers']))
    #print(conjugator.conjugate("jump over", number=conjugator.PLURAL, person=conjugator.THIRD_PERSON, tense=conjugator.PRESENT_TENSE))
    #print(interpreter.stanford_pos("King of Germans"))
    #print("final: ", sentence_planner.traverse_and_check("university", memory.CURRENT_CONTEXT, [],[]))
    #print(sentence_planner.plan_randomly_from_memory("", 2))
    #memory.save_memory("memory1.yml")
    return render(request, 'messenger/index.html', context)

def select(request):
    yaml = YAML(typ='safe')
    list_context = [x for x in os.listdir(CONTEXT_DIR)]
    l_details = []
    for x in list_context:
        a = yaml.load(open(CONTEXT_DIR + x + '\\' + "context_plan.yml", 'r'))['description']
        a['id'] = x
        l_details.append(a)
    context = {'context_list':l_details}
    return render(request, 'messenger/select.html', context)

def converse(request, context_id):
    #memory.read_context(context_id)
    #context = {'introduction':dialogue_manager.introduce()}
    logger.save_log()
    return render(request, 'messenger/converse.html', context)

def process_message(request):
#    user = None
#    if request.user.is_authenticated():
#        user = request.user.id
    message = json.loads(request.body.decode('utf-8'))['message']
    logger.log("User", message)
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
    #output_message = response_planner.plan_response(message, {'num_sentences': 10, 'stutter':0})
    output_message = dialogue_manager.reply(message)
    logger.log(memory.CURRENT_STATE['character'], output_message)
    data = {'response': output_message}
    return JsonResponse(data)
