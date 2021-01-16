from django.db import models
import hashlib

# Create your models here.

#Decided that another db is not required because the hash for the databases and the source code is generated each time anyway.
class BlockStructure(models.Model):
     BlockNo= models.IntegerField(unique=True,null=False,blank=False)
     ParentHash=models.CharField(max_length=200, null=True, blank=False, default=None)

class BBlock(models.Model):
     
     block_hash = models.CharField(max_length=128, null=False, blank=False)
     parent_hash = models.CharField(max_length=128, null=False, blank=False)
     database_hash = models.TextField(blank=False)
     hash_of_database_hash = models.CharField(max_length=128, null=False, blank=False)
     source_code_hash = models.TextField(blank=False)
     hash_of_source_code_hash = models.CharField(max_length=128, null=False, blank=False)
     candidate_votes = models.TextField(blank=True, null=True)
     electors = models.TextField(blank=True,null=True)
     timestamp_iso = models.CharField(max_length=30, null=False, blank=False)
     total_votes = models.IntegerField(null=False, blank=False)
     reason = models.CharField(max_length=200, null=True, blank=True)

     @property
     def isGenesis(self):
          if self.parent_hash == '0'.zfill(128):
               return True
          return False

     def calculateHash(self):
          m = hashlib.sha512()
          m.update(self.parent_hash.encode("utf-8"))
          m.update(self.database_hash.encode("utf-8"))
          m.update(self.source_code_hash.encode("utf-8"))
          m.update(self.candidate_votes.encode("utf-8"))
          m.update(self.electors.encode("utf-8"))
          m.update(self.reason.encode("utf-8"))
          m.update(self.timestamp_iso.encode("utf-8"))
          m.update(str(self.total_votes).encode("utf-8"))
          return m.hexdigest()

     def calculateHashOfDatabaseHash(self):
          m = hashlib.sha512()
          m.update(self.database_hash.encode("utf-8"))
          return m.hexdigest()

     def calculateHashOfSourceCodeHash(self):
          m = hashlib.sha512()
          m.update(self.source_code_hash.encode("utf-8"))
          return m.hexdigest()
