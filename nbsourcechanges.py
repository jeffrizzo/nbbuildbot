
"""
Parse NetBSD source-changes (or source-changes-full)email.
"""
import re
import datetime

from twisted.python import log

from email.utils import parsedate_tz, mktime_tz
from email.iterators import body_line_iterator
from buildbot import util
from buildbot.changes.mail import MaildirSource


class NBCVSMaildirSource(MaildirSource):
    name = "NBCVSMaildirSource"

    def __init__(self, maildir, prefix=None, category='',
                 repository='', properties={}):
        MaildirSource.__init__(self, maildir, prefix, category, repository)
        self.properties = properties

    def parse(self, m, prefix=None):
        """Parse messages sent by the NetBSD source-changes mailing list.
        """

        log.msg('Processing source-changes mail')
        match=re.match('^CVS commit:\s*(\[(.+)\])?',m["Subject"])
        if match:
            if match.groups():
                branch = match.group(2)
            else:
                branch = None
        else:
            log.msg('source-changes: returning early #1')
            return None

        # handle source-changes-all, which is multipart
        while m.is_multipart():
            log.msg('source-changes: mail is multipart')
            m = m.get_payload(0)

        authorRE        = re.compile( '^Committed By:\s*(\S.*)')
        brokenlineRE    = re.compile( '\\[\r\n]*$')
        dateRE          = re.compile( '^Date:\s*(\S.*)')
        diffRE          = re.compile( '^To generate a diff of this commit:')
        filesRE         = re.compile( '^cvs rdiff -u -r\S+ -r\S+(\s.*)')
        comments = ""
        cvsroot = 'anoncvs@anoncvs.netbsd.org:/cvsroot'
        files = []
        is_dir = 0

        # Assumptions:
        # - the files all live between diffRE and pleaseRE
        # - only lines in that section are continued

        lines = list(body_line_iterator(m))
        while lines:
            line = lines.pop(0)
            m = authorRE.match(line)
            if m:
                author = m.group(1)
                continue
            m = dateRE.match(line)
            if m:
                # calculate a "revision" based on date
                # or the current time
                # if we're unable to parse the date.
                dateTuple = parsedate_tz(m.group(1))
                if dateTuple == None:
                    when = util.now()
                else:
                    when = mktime_tz(dateTuple)
                theTime =  datetime.datetime.utcfromtimestamp(float(when))
                rev = theTime.strftime('%Y-%m-%d %H:%M:%S')
                continue
            if line == "Log Message:\n":
                break

        while lines:
            line = lines.pop(0)
            while brokenlineRE.match(line) != None:
                line = line[:-1] + lines.pop(0)
            if diffRE.match(line):
                break
            comments += line

        while lines:
            line = lines.pop(0)
            m = filesRE.match(line)
            if m:
                f = re.findall('\S+',m.group(1))
                files = files + f

        comments = comments.rstrip() + "\n"
        if comments == '\n':
            comments = None

        category = self.getCategory(files)
        log.msg('source-changes: got to end, author is %s' % author)
        return ('cvs', dict(author=author, files=files, comments=comments,
                            isdir=is_dir, when=when, branch=branch,
                            revision=rev, category=category,
                            repository=cvsroot, project='NetBSD',
                            properties=self.properties))

    def getCategory(self, files):
        archRE      =   re.compile('^src/(sys/arch|distrib)/([^/])')
        distribRE   =   re.compile('^src/distrib/')
        kernelRE    =   re.compile('^src/sys/')

        for f in files:
            result = {}
            m = archRE.match(f)
            if m:
                result[m.group(2)] = True
            m = distribRE.match(f)
            if m:
                result['distrib'] = True
                continue
            m = kernelRE.match(f)
            if m:
                result['kernel'] = True
                continue

        resultstring = ""
        for k in result.keys():
            resultstring += "%s." % k

        return resultstring


    def getProject(self, files):
        pass
