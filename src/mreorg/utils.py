#----------------------------------------------------------------------
# Copyright (c) 2012 Michael Hull.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions 
# are met:
#
#  - Redistributions of source code must retain the above copyright 
#    notice, this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in 
#    the documentation and/or other materials provided with the 
#    distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS 
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE 
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, 
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT 
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
# WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.
#----------------------------------------------------------------------

import inspect
import os

import hashlib
import tokenize, token


class ScriptUtils(object):

    @classmethod
    def get_calling_script(cls):
        frame = inspect.stack()

        callee_frame = frame[-1]
        callee_file = callee_frame[1]
        return callee_file

    @classmethod
    def get_calling_script_directory(cls):
        return  os.path.dirname( cls.get_calling_script() )

    @classmethod
    def get_calling_script_file(cls, include_ext):
        filename = os.path.basename( cls.get_calling_script() )
        if include_ext:
            return filename
        else:
            return os.path.splitext(filename)[0]





    ## Deprecated:
    ## ##################################
    #outputStoreDir = "_output_store/"
    #currentOutputLinkDir =  "_out"
    ## We store the Full iso format of when the simulation was run, as
    ## well as the shortedn
    #now = datetime.datetime.now()
    #datetimestringISO = now.isoformat()
    #datetimestringInformal = now.strftime("[%a %d %B - %I:%M]")
    #datetimestr = "%s_%s/"%( datetimestringISO, datetimestringInformal )

    #@classmethod
    #def getOutputDir(cls):
    #    assert False, "To be removed June 2012"
    #    dirName = cls.outputStoreDir + cls.datetimestr
    #    fullDirName = join( cls.get_calling_script_directory(), dirName )
    #    ensure_directory_exists(fullDirName)
    #    return fullDirName


    #@classmethod
    #def updateLinkToOutputDir(cls):
    #    assert False, "To be removed June 2012"
    #    opDir = cls.getOutputDir()
    #    fullLinkName = os.path.join( 
    #            cls.get_calling_script_directory(), 
    #            cls.currentOutputLinkDir )
    #    if exists( fullLinkName ):
    #        os.unlink( fullLinkName )

    #    os.system("""ln -s "%s" "%s" """%(opDir, fullLinkName) )





def extract_docstring_from_fileobj(fileobj):
    for token_data in tokenize.generate_tokens(fileobj.readline):
        tok = token_data[0]
        text = token_data[1]
        if tok in [tokenize.COMMENT, tokenize.NL]:
            continue
        elif tok in [tokenize.NAME, tokenize.ENDMARKER]:
            return None
        elif tok == tokenize.STRING:
            text = text.strip()
            if text.startswith('"""'):
                text = text[3:]
            if text.endswith('"""'):
                text = text[:-3]
            return text.strip()
        else:
            tokenname = token.tok_name[tok]
            raise ValueError('Unexpected token %s (%s)'%(tokenname, tok))
    return None




def ensure_directory_exists(filename):
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname) and dirname.strip():
        os.makedirs(dirname)
    return filename


# Refactor to another file:
# ############################
def get_file_sha1hash(filename):
    hashObj = hashlib.sha1()
    with  open(filename) as f:
        hashObj.update( f.read() )
    return hashObj.hexdigest()

# #################################


