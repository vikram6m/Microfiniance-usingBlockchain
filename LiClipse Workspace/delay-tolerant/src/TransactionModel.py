class TransactionModel:
    def __init__(self, uniqueID=0, effDate=None, fromAccountID="", toAccountID="",amount=0,prevHash="", hash="", isBlockChainGenerated=0, fromAccountModel=None,toAccountModel=None):
        self.uniqueID = uniqueID
        self.effDate = effDate
        self.fromAccountID = fromAccountID
        self.toAccountID = toAccountID
        
        self.amount = amount
        self.prevHash = prevHash
        self.hash = hash
        self.isBlockChainGenerated = isBlockChainGenerated
        self.fromAccountModel = fromAccountModel
        self.toAccountModel = toAccountModel
