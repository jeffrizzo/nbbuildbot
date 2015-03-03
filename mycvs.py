import os.path

__author__ = 'jrizzo'


class MyCVS(CVS):
    def __init__(self, **kwargs):
        CVS.__init__(self, **kwargs)

    # Override the doCheckout method with one that tries to handle workdir
    # better.
    def doCheckout(self, dir):
        (workdir, module) = os.path.split(dir)
        command = ['-d', self.cvsroot, '-z3', 'checkout', '-d', module]
        command = self.global_options + command + self.extra_options
        if self.branch:
            command += ['-r', self.branch]
        if self.revision:
            command += ['-D', self.revision]
        command += [self.cvsmodule]
        d = self._dovccmd(command, workdir)
        return d

    def doUpdate(self):
        command = self.global_options + ['-z3', 'update', '-dP']
        branch = self.branch
        # special case. 'cvs update -r HEAD -D today' gives no files; see #2351
        if branch == 'HEAD' and self.revision:
            branch = None
        if (not branch) and (not self.revision):
            command += ['-A'] # reset tag
        if branch:
            command += ['-r', self.branch]
        if self.revision:
            command += ['-D', self.revision]
        d = self._dovccmd(command)
        return d