from django.core.serializers.json import DjangoJSONEncoder
from election.models import ElectionConfig, Candidate, Elector, Position
from vote.models import Voted, CandidateVote
from chain.models import BBlock
from django.contrib.auth.models import User
import hashlib
import json
import os
from ballotblock import settings
from django.db import transaction, DatabaseError
import datetime
from election.business import ElectionBusiness
from decimal import Decimal

class HashCalculator():

    def databaseHash(self):
        hash_dict = {}

        # Include hash for Election Config
        queryset = list(ElectionConfig.objects.all().values('id', 'description', 'start_time', 'end_time', 
                        'block_time_generation', 'guess_rate', 'min_votes_in_block', 'min_votes_in_last_block',
                        'attendance_rate', 'locked').order_by('id'))
        cs_json_str = json.dumps(queryset, cls=DjangoJSONEncoder)
        m = hashlib.sha512()
        m.update(cs_json_str.encode("utf-8"))
        hash_dict["election_config"] = queryset
        hash_dict["election_config_hash"] = m.hexdigest()
        

        # Include hash for Candidates
        queryset = list(Candidate.objects.all().values('id', 'name', 'position_id').order_by('id'))
        cs_json_str = json.dumps(queryset, cls=DjangoJSONEncoder)
        m = hashlib.sha512()
        m.update(cs_json_str.encode("utf-8"))
        hash_dict["candidates"] = queryset
        hash_dict["candidates_hash"] = m.hexdigest()

        # Include hash for Positions
        queryset = list(Position.objects.all().values('id', 'description', 'quantity').order_by('id'))
        cs_json_str = json.dumps(queryset, cls=DjangoJSONEncoder)
        m = hashlib.sha512()
        m.update(cs_json_str.encode("utf-8"))
        hash_dict["positions"] = queryset
        hash_dict["positions_hash"] = m.hexdigest()

        # Include hash for Electors
        queryset = list(Elector.objects.all().values('id', 'user_id').order_by('id'))
        cs_json_str = json.dumps(queryset, cls=DjangoJSONEncoder)
        m = hashlib.sha512()
        m.update(cs_json_str.encode("utf-8"))
        hash_dict["electors"] = queryset
        hash_dict["electors_hash"] = m.hexdigest()

        # Include hash for Users
        queryset = list(User.objects.all().values('id', 'first_name', 'last_name', 'email', 'is_superuser').order_by('id'))
        cs_json_str = json.dumps(queryset, cls=DjangoJSONEncoder)
        m = hashlib.sha512()
        m.update(cs_json_str.encode("utf-8"))
        hash_dict["users"] = queryset
        hash_dict["users_hash"] = m.hexdigest()

        d = {"database":hash_dict}

        return json.dumps(d, cls=DjangoJSONEncoder)

    def __ignoreFile(self, filename):
        if filename.endswith('.py'):
            return False
        if filename.endswith('.js'):
            return False
        if filename.endswith('.css'):
            return False
        if filename.endswith('.html'):
            return False
        return True

    def sourceCodeHash(self):
        BUF_SIZE = 65536
        source_list = []

        for root, dirs, files in os.walk(settings.BASE_DIR):
            for filename in files:
                if not os.path.isdir(os.path.join(root, filename)):
                    if not self.__ignoreFile(str(filename)):
                        m = hashlib.sha512()
                        with open(os.path.join(root, filename), 'rb') as f:
                            while True:
                                data = f.read(BUF_SIZE)
                                if not data:
                                    break
                                m.update(data)
                        source_list.append({"file": os.path.join(root, filename), "file_hash": m.hexdigest()})
        
        d = {"source_code": source_list} 

        return json.dumps(d, cls=DjangoJSONEncoder)

class BBlockHandler():

    def shouldAddBlock(self):
        eb = ElectionBusiness()
        # While election is occurring, new blocks should be generated.
        if eb.isOccurring():
            return True
        if eb.isLocked() and eb.hadFinished():
            return True
        ec = eb.getCurrentElectionConfig()
        if not ec:
            raise DatabaseError('There is not Election Configuration for the current election')
        # Independently of election is occurring, if we have votes, a new block must be generated.
        if Voted.objects.filter(hash_val__isnull=True).count() > 0:
            return True
        # If election is not occurring and we do not have votes we do not need to generate a block.
        return False
    
    def shouldAddLastBlock(self):
        if self.isLastBlock():
            if Voted.objects.count() == Elector.objects.count():
                return True
        eb = ElectionBusiness()
        if eb.isLocked() and eb.hadFinished():
            return True

        return False
    
    def isLastBlock(self):
        eb =  ElectionBusiness()
        if self.shouldAddBlock():
            ec = eb.getCurrentElectionConfig()
            if (Voted.objects.count()-ec.min_votes_in_last_block)/Elector.objects.count() > ec.attendance_rate:
                return True
        if eb.isLocked() and eb.hadFinished():
            return True
        return False
    
    def checkMinVotes(self, bblock):
        ec = ElectionBusiness().getCurrentElectionConfig()
        if self.shouldAddBlock():
            electors = json.loads(bblock.electors)
            if self.isLastBlock():
                if self.shouldAddLastBlock():
                    return True
            if (len(electors) * Position.objects.count()) >= ec.min_votes_in_block:
                return True
        return False
    
    def checkGuessRate(self, bblock):
        ec = ElectionBusiness().getCurrentElectionConfig()
        last_public_block = BBlock.objects.filter(reason='').order_by('-timestamp_iso')[0]
        max_difference = 0
        i = 0
        cv = json.loads(bblock.candidate_votes)
        pcv = json.loads(last_public_block.candidate_votes)
        while i < len(cv):
            if cv[i]['quantity'] - pcv[i]['quantity'] > max_difference:
                max_difference = cv[i]['quantity'] - pcv[i]['quantity']
            i = i + 1
        
        guess_rate = max_difference / ((bblock.total_votes - last_public_block.total_votes) / Position.objects.count())
        if Decimal(str(guess_rate)) <= ec.guess_rate:
            return True

        return False

    def shouldIncludeElectors(self, bblock):
        if self.shouldAddLastBlock():
            return (True, '')
            
        if not self.checkMinVotes(bblock):
            return (False, 'Number of electors rule is not attended.')
        if not self.checkGuessRate(bblock):
            return (False, 'Guess rate rule is not attended.')
        return (True, '')


    def add(self):
        if not self.shouldAddBlock():
            return

        finish_election = False
        if self.shouldAddLastBlock():
            finish_election = True

        if BBlock.objects.all().count() == 0:
            raise DatabaseError('It is not possible to add a block without genesis block')
            
        previous_block = BBlock.objects.all().order_by('-timestamp_iso')[0]

        # Put these outside the transaction
        hc = HashCalculator()
        database_hash = hc.databaseHash()
        source_code_hash = hc.sourceCodeHash()

        # Get the last block which has electors divulged.
        last_public_block = BBlock.objects.filter(reason='').order_by('-timestamp_iso')[0]

        with transaction.atomic():
            #bblock = BBlock.objects.create()
            bblock = BBlock()
            bblock.database_hash = database_hash
            bblock.hash_of_database_hash = bblock.calculateHashOfDatabaseHash()
            bblock.source_code_hash = source_code_hash
            bblock.hash_of_source_code_hash = bblock.calculateHashOfSourceCodeHash()
            
            bblock.timestamp_iso = datetime.datetime.now().isoformat()
            same_qtt_votes = False
            cv_quantity = 0

            while not same_qtt_votes:
                # Workaround to lock electors who will be locked.
                #Voted.objects.filter(hash_val__isnull=True).update(hash_val='x')
                #electors = list(Voted.objects.filter(hash_val='x').values('id', 'elector_id', 'system_signature').order_by('id'))
                electors = list(Voted.objects.filter(hash_val__isnull=True).values('id', 'elector_id', 'system_signature').order_by('id'))
                candidate_votes = list(CandidateVote.objects.all().values('id', 'candidate_id', 'quantity').order_by('id'))
                cv_quantity = self.__count_votes(candidate_votes)
                if (cv_quantity - last_public_block.total_votes) == (len(electors) * Position.objects.count()):
                    same_qtt_votes = True
            
            elector_id_list = []
            for e in electors:
                elector_id_list.append(e['id'])

            bblock.candidate_votes = json.dumps(candidate_votes, cls=DjangoJSONEncoder)
            bblock.electors = json.dumps(electors, cls=DjangoJSONEncoder)
            bblock.parent_hash = previous_block.block_hash
            bblock.total_votes = cv_quantity

            ret = self.shouldIncludeElectors(bblock)
            if not ret[0]:
                bblock.electors = json.dumps([], cls=DjangoJSONEncoder)
                bblock.reason = ret[1]
                bblock.block_hash = bblock.calculateHash()
            else:
                bblock.reason = ''
                bblock.block_hash = bblock.calculateHash()
                Voted.objects.filter(id__in=elector_id_list).update(hash_val=bblock.block_hash)

            bblock.save()

            if finish_election:
                ec = ElectionBusiness().getCurrentElectionConfig()
                ec.locked = False
                ec.save()

    def __count_votes(self, candidate_votes):
        cv_quantity = 0
        for cv in candidate_votes:
            cv_quantity += cv['quantity']
        return cv_quantity

    
    def add_genesis(self):

        hc = HashCalculator()
        database_hash = hc.databaseHash()
        source_code_hash = hc.sourceCodeHash()

        with transaction.atomic():
            bblock = BBlock()
            bblock.database_hash = database_hash
            bblock.hash_of_database_hash = bblock.calculateHashOfDatabaseHash()
            bblock.source_code_hash = source_code_hash
            bblock.hash_of_source_code_hash = bblock.calculateHashOfSourceCodeHash()
            bblock.electors = json.dumps(list(Voted.objects.all().values('id', 'elector_id', 'system_signature').order_by('id')), cls=DjangoJSONEncoder)
            bblock.candidate_votes = json.dumps(list(CandidateVote.objects.all().values('id', 'candidate_id', 'quantity').order_by('id')), cls=DjangoJSONEncoder)
            bblock.timestamp_iso = datetime.datetime.now().isoformat()
            bblock.total_votes = 0
            bblock.reason=''
            bblock.parent_hash = '0'.zfill(128)
            bblock.block_hash = bblock.calculateHash()
            bblock.save()
