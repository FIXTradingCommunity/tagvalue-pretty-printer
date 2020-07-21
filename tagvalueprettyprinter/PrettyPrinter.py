class PrettyPrinter():

    def __init__(self):
        '''Initialize fix with fcgm properties'''

        from pyfixorchestra import FixDictionary

        field = FixDictionary('fields')
        self.fields = (field.generateDictionary()) # [names, temp]

        component = FixDictionary('components')
        self.components = (component.generateDictionary()) # [names, miniIDs, miniGroup, miniComp, temp]
        group = FixDictionary('groups')
        self.groups = (group.generateDictionary()) # [names, numInGroup, miniIDs, miniGroup, miniComp, temp]

        message = FixDictionary('messages')
        self.messages = (message.generateDictionary()) # [names, miniIDs, miniGroup, miniComp, temp]

        self.level = 1
        self.context_list = []  # List of IDs that define context.
        self.context = []  # List of 2 items - tag, type(ie mcgf)
        self.allowed = []  # List of lists of allowed field,group,comp,numingrp
        self.output_string = []  # tag value level

    def get_allowed(self):
        '''Takes current context value and type, and returns allowed fields, groups and components'''

        context = self.context[0]
        feature = self.context[1]
        if feature == 'm':
            allowed_fields = self.messages[context][1]
            allowed_groups = self.messages[context][2]
            allowed_comps = self.messages[context][3]
            allowed_numingroup = []
        elif feature == 'c':
            allowed_fields = self.components[context][1]
            allowed_groups = self.components[context][2]
            allowed_comps = self.components[context][3]
            allowed_numingroup = []
        else:
            allowed_numingroup = self.groups[context][1]
            allowed_fields = self.groups[context][2]
            allowed_groups = self.groups[context][3]
            allowed_comps = self.groups[context][4]
        return  ([allowed_fields, allowed_groups,allowed_comps, allowed_numingroup])

    def check_in_subfields(self, tv):
        '''Checks if the tag is in currently allowed fields'''
        return (tv[0] in self.allowed[0], '0')

    def check_in_subcomponents(self, tv):
        '''Checks if the tag is inside currently allowed components'''
        for c in self.allowed[2]:
            if tv[0] in self.components[c][1]:  # If tag is in component's fields
                return (True, c) # Return true and the component that contains this tag
        return (False, '0')

    def check_in_subgroups(self, tv):
        '''Checks if the tag is a numingroup inside currently allowed groups'''
        for g in self.allowed[1]:
            if tv[0] in self.groups[g][1]:  # If tag is in groups's numingroup
                return (True, g) # Return true and the group that contains this tag
        return (False, '0')

    def check_in_subs(self, tv):
        '''checks for tv in fields, subcomponents, subgroups. Appends output_str and returns True if found'''

        in_sub_field = self.check_in_subfields(tv)
        in_sub_comp = self.check_in_subcomponents(tv)
        in_sub_group = self.check_in_subgroups(tv)

        # Check in sub fields
        if in_sub_field[0]:
            self.out(tv, self.level,'field')
            return True

        # Check in sub components
        elif in_sub_comp[0]:
            self.level += 1
            self.context = [in_sub_comp[1], 'c']
            self.context_list.append(self.context)
            self.allowed = self.get_allowed()
            self.out(tv, self.level,'component',self.components[self.context[0]][0])
            return True

        # Check in sub group
        elif in_sub_group[0]:
            self.level += 1
            self.context = [in_sub_group[1], 'g']
            self.context_list.append(self.context)
            self.allowed = self.get_allowed()
            self.out(tv, self.level-1,'numingrp',self.groups[self.context[0]][0])
            return True

        else:
            return False

    def out(self, tv, level, typee, name = None):
        '''Appends tag, value, level, type and name to tag value list'''
        tv.append(level)
        tv.append(typee)
        if name:
            tv.append(name)
        self.output_string.append(tv)

    def get_level(self, msg):
        '''Takes in 1 line of FIX message as list of lists, returns list of lists with levels appended'''

        flag35 = False

        for tv in msg:

            # For StandardHeader - level = 1. Level is appended to tag value list, index 2
            if not flag35:
                self.out(tv, self.level, 'component')

            # msgtype - sets context based on msgname, gets allowed fgc
            if tv[0] == '35':
                flag35 = True
                self.context = [tv[1], 'm']  # type - message
                self.context_list.append(self.context)
                self.allowed = self.get_allowed()

            if flag35 and tv[0] != '35':

                bol = self.check_in_subs(tv)

                # Go back one context if tag not found in current context
                # Setting a count to avoid infinite loops
                ct = 1
                while not bol and ct < 30:
                    ct += 1
                    self.level -= 1
                    if self.level < 1:
                        print(f'Out of bounds! Check tag {tv[0]}')
                        break
                    self.context_list.pop()
                    self.context = self.context_list[-1]
                    self.allowed = self.get_allowed()
                    bol = self.check_in_subs(tv)
        return(self.output_string)

    def prettify(self,logfile):
        '''COnsolidated function. Takes logfine as input, pretty prints messages'''
        outp = self.parse(logfile)
        self.prettyprint(outp)

    def parse(self, logfile):
        '''Parses log file, returns list of tag values in list of tag value lines'''
        with open(logfile, 'r') as f:
            lines = f.readlines()
            delim = self.get_delim(lines)
            tagvalue_lines = []
            for line in lines:

                line = line.replace('\u2028447','') # Replaces this pesky unicode
                strt_idx = line.find('8=FIX')
                line=line[strt_idx:]
                columns = line.split(delim)
                tagvalue = []
                for col in columns:
                    values = col.split('=')
                    if len(values) > 1: # This ignores all \n
                        tagvalue.append([values[0],values[1]])
                tagvalue_lines.append(tagvalue)
        return tagvalue_lines

    def get_delim(self, lines):
        '''Finds delimiter for given FIX messages'''
        i = 0
        delim = ''
        while delim not in ['<SOH>',':',';','^',' ','|'] and i<10:
            try:
                if '<SOH>' in lines[i]:
                    delim = '<SOH>'
                else:
                    delim_idx = lines[i].rfind('10=')
                    delim = lines[i][delim_idx-1]
            except:
                print("Error: couldn't find delimiter in line ", i)
            i+=1
        return delim

    def prettyprint(self,tagvalue_lines):
        '''Takes in levels, types and name for tags and values, prints output'''

        for line in tagvalue_lines:
            print() # Blank line
            print('New message')
            print('\t--- StandardHeader component')

            line_with_level = self.get_level(line)

            for tagvalue in line_with_level:
                try:
                    key = tagvalue[0]
                    level = tagvalue[2]
                    keyname = self.fields[key][0]

                    if key == '35': # If message
                        try:
                            msg_name = self.messages[tagvalue[1]][0]
                            print(level*'\t'+'  '+f'{keyname}({key}) = {msg_name}({tagvalue[1]})')
                        except KeyError:
                            print(f'No message name listed for 35 = {tagvalue[1]}')
                            print(level*'\t'+f'{keyname}({key}) = ({tagvalue[1]})')
                    else:
                        # Printing components
                        if tagvalue[3] == 'component':
                            if level <= 1: # Applicable to level 1 components only
                                level = 2
                            if len(tagvalue)>4:
                                print((level-1)*'\t'+f'--- {tagvalue[4]} component') # Component name
                            print((level-1)*'\t'+'  '+f'{keyname}({key}) = {tagvalue[1]}')
                        # Printing groups
                        elif tagvalue[3] == 'numingrp':
                            print(level*'\t'+f'--- {tagvalue[4]} group') # Group name
                            print(level*'\t'+f'{keyname}({key}) = {tagvalue[1]}')

                        else:
                            print(level*'\t'+f'{keyname}({key}) = {tagvalue[1]}')

                except:
                    print(f'key name not found for tag {key}')
            self.level = 1 # reset level after every message
