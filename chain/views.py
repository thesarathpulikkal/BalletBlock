from django.shortcuts import render, redirect
from chain.business import BBlockHandler
from chain.models import BBlock
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.core import serializers
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.core.paginator import Paginator
from election.models import Position, Candidate

def block_list(request, template_name='block_list.html'):
    bblocks = BBlock.objects.all()
    paginator = Paginator(bblocks, 3) # Show 3 contacts per page
    page = request.GET.get('page')
    bblock_list = paginator.get_page(page)

    genesis_block = None
    if bblocks.count() > 0:
        genesis_block = BBlock.objects.filter(parent_hash='0'.zfill(128))[0]
    return render(request, template_name, {'bblock_list': bblock_list, 'genesis_block': genesis_block, 'paginator':paginator})

def block_add(request):
    BBlockHandler().add()
    return redirect('block_list')

def database_hash(request, bblock_id, template_name='database_hash.html'):
    bblock = BBlock.objects.get(id=int(bblock_id))
    database_hash_dict = json.loads(bblock.database_hash)
    genesis_block = BBlock.objects.filter(parent_hash='0'.zfill(128))[0]
    genesis_database_hash_dict = json.loads(genesis_block.database_hash)
    return render(request, template_name, {'bblock': bblock, 'genesis_block': genesis_block,
             'database_hash_dict': database_hash_dict, 'genesis_database_hash_dict': genesis_database_hash_dict})

def source_code_hash(request, bblock_id, template_name='source_code_hash.html'):
    bblock = BBlock.objects.get(id=int(bblock_id))
    source_code_hash_dict = json.loads(bblock.source_code_hash)
    genesis_block = BBlock.objects.filter(parent_hash='0'.zfill(128))[0]
    diff_files = []
    if bblock.source_code_hash != genesis_block.source_code_hash:
        genesis_source_code_hash_dict = json.loads(genesis_block.source_code_hash)
        for f in source_code_hash_dict['source_code']:
            if f not in genesis_source_code_hash_dict['source_code']:
                diff_files.append(f['file'])
    return render(request, template_name, {'bblock': bblock, 'genesis_block': genesis_block,
             'source_code_hash_dict': source_code_hash_dict, 'diff_files':diff_files })


def validate_chain(request):
    valid = True
    parent_hash = '0'.zfill(128)
    genesis_block = BBlock.objects.all().order_by('timestamp_iso')[0]
    for bblock in BBlock.objects.all().order_by('timestamp_iso'):
        if bblock.parent_hash != parent_hash:
            messages.error(request, mark_safe('Parent hash does not match<br>Block parent hash: {}<br>Parent hash: {}'.format(bblock.parent_hash, 
                                parent_hash)) )
            valid = False
        parent_hash = bblock.block_hash
        calculated_hash = bblock.calculateHash()
        if bblock.block_hash != calculated_hash:
            messages.error(request, mark_safe('Block hash does not match<br>Stored hash: {}<br>Calculated hash: {}'.format(bblock.block_hash, 
                                calculated_hash)) )
            valid = False
        if bblock.hash_of_database_hash != genesis_block.hash_of_database_hash:
            messages.error(request, mark_safe('Database hash does not match<br>Database hash of block: {}<br>Genesis Block database hash: {}'.format(bblock.hash_of_database_hash, 
                                genesis_block.hash_of_database_hash)) )
            valid = False
        if bblock.hash_of_source_code_hash != genesis_block.hash_of_source_code_hash:
            messages.error(request, mark_safe('Source code hash does not match<br>Source code hash of block: {}<br>Genesis Block source code hash: {}'.format(bblock.hash_of_source_code_hash, 
                                genesis_block.hash_of_source_code_hash)) )
            valid = False
    if valid:
        messages.success(request, 'Chain is valid')
    return redirect('block_list')


def block_election_result(request, bblock_id, template_name='block_election_result.html'):
    bblock = BBlock.objects.get(id=int(bblock_id))
    candidate_votes_dict = json.loads(bblock.candidate_votes)
    
    data = []
    position_list = []
    positions = Position.objects.all()
    for p in positions:
        for cv in candidate_votes_dict:
            candidate = Candidate.objects.get(id=int(cv['candidate_id']))
            if candidate.position == p:
                position_list.append({'candidate__name':candidate.name,
                        'candidate__position__description': p.description,
                        'quantity': cv['quantity']
                        })
        data.append(json.dumps(position_list, cls=DjangoJSONEncoder) )
        position_list = []
    '''
    for p in positions:
        candidate_vote = CandidateVote.objects.filter(candidate__position=p).values('candidate__name', 'candidate__position__description', 'quantity' )
        candidate_vote_json_str = json.dumps(list(candidate_vote), cls=DjangoJSONEncoder)
        data.append(candidate_vote_json_str)
    '''
  
    return render(request, template_name, context={'results_data':json.dumps(data, cls=DjangoJSONEncoder), 'positions':positions})