import streamlit as st
import pandas as pd
import numpy as np
import random
import re

st.set_page_config(layout="wide")

if "cards" not in st.session_state:
    st.session_state['cards'] = {}

if "riders" not in st.session_state:
    st.session_state.riders = []

if "riders2" not in st.session_state:
    st.session_state.riders2 = []

if "rdf" not in st.session_state:
    st.session_state['rdf'] = pd.DataFrame()

if "gcdf" not in st.session_state:
    st.session_state['gcdf'] = pd.DataFrame()

if "placering" not in st.session_state:
    st.session_state['placering'] = 0

if "ryttervalg2" not in st.session_state:
    st.session_state.ryttervalg2 = 'select'

if "ryttervalg" not in st.session_state:
    st.session_state.ryttervalg = 'select'

if "human_chooses_cards" not in st.session_state:
    st.session_state.human_chooses_cards = 9

if "ready_for_calculate" not in st.session_state:
    st.session_state.ready_for_calculate = False

if "computer_chooses_cards" not in st.session_state:
    st.session_state.computer_chooses_cards = True

if "goto3" not in st.session_state:
    st.session_state.goto3   = False

def visrytterkort(ryttervalg):
    a, b, c, d = random.sample(range(len(cards[ryttervalg]['cards'])), 4)
    col1.radio('hvilket kort?',
                   (cards[ryttervalg]['cards'][a], cards[ryttervalg]['cards'][b], cards[ryttervalg]['cards'][c], cards[ryttervalg]['cards'][d]))


def has_numbers(inputString):
    return bool(re.search(r'\d', inputString))

def convert_to_seconds(number):
    number = number + random.randint(int(-number**+.5),int(number**+.5))
    minutes = int(np.floor(number/60))
    seconds = str(int(np.floor(number - minutes*60)))
    if len(seconds)<2:

        seconds = "0" + seconds
    return (str(minutes)+':'+str(seconds))

def convert_to_seconds_plain(number):

    minutes = int(np.floor(number/60))
    seconds = str(int(np.floor(number - minutes*60)))
    if len(seconds)<2:

        seconds = "0" + seconds
    return (str(minutes)+':'+str(seconds))

def tjek_bakke(pos1, pos2, track):
    pos1 = int(pos1)
    pos2 = int(pos2)
    if '^' in track[pos1:pos2]:
        return 1
    else:
        return 0


def get_length(track):
    tr = track[0:track.find('F')]
    tr = tr.replace('-', '6')
    tr = tr.replace('_', '9')

    tr = list(tr)

    for i in reversed(range(len(tr))):
        # print(char)
        if tr[i] in ['1', '2', '3', '4', '5']:
            last = tr[i]

        if tr[i] == '^':
            tr[i] = last

    sum = 0
    for number in tr:
        sum = int(number) + sum

    #sum
    # tr = tr.replace('^',last)

    for number in tr[-13::]:
        sum = sum - int(number) * 0.23
        #print(number)

    sum = sum / 6
    return int(sum)



def check_vedhang(moved_fields, pos2, track):
    pos1 = pos2 - moved_fields
    vedhang = 0
    if has_numbers(track[pos1:pos2]):
        vedhang = int(list(filter(str.isdigit, track[pos1:pos2]))[0])

    return vedhang


def sprint(sprint_group, cards, df):
    for rider in cards:
        if cards[rider]['group'] == sprint_group:
            for card in cards[rider]['discarded']:
                cards[rider]['cards'].append(card)
            cards[rider]['discarded'] = []
            random.shuffle(cards[rider]['cards'])

            cards_available = []
            for i in range(0, min(4, len(cards[rider]['cards']))):
                cards_available.append(cards[rider]['cards'][i][1])

            while len(cards_available) < 4:
                cards_available.append(2)

            cards_available.sort(reverse=True)
            #st.write(rider, cards[rider]['sprint'], cards_available)
            cards[rider]['sprint_points'] = cards[rider]['sprint'] * 1.05 + cards_available[0] + cards_available[1] + \
                                            cards_available[2] * 0.01 + cards_available[1] * 0.001
            #st.write(cards[rider]['sprint_points'])

    sorted(cards.items(), key=lambda item: (item[1]["sprint_points"]), reverse=True)

    col3.header('SPRINT: GROUP ' + str(sprint_group))

    for rider in sorted(cards.items(), key=lambda item: (item[1]["sprint_points"]), reverse=True):
        # print(, 'points')
        if cards[rider[0]]['group'] == sprint_group:
            st.session_state['placering'] = st.session_state['placering'] + 1
            col3.caption(str(rider[0]) + ' - ' + str(int(cards[rider[0]]['sprint_points'])) + ' ' + 'sprint points')
            cards[rider[0]]['ranking'] = st.session_state['placering']

    return cards


def do_everything(df):

    with col3:
        #df['position'] = df['position'] + df['moved_fields']
        # move riders
        #df['takes_lead'] = np.random.randint(0, 2, df.shape[0])
        df = df.sort_values(by='old_position', ascending = False)
        st.header('1. MOVE')
        df['tl2'] = df['takes_lead'] * df['position']

        for i in range(1, df['group'].max() + 1):
            print(i)
            df.loc[df['group'] == i, ['tl2']] = df[df['group'] == i].tl2.max()

        # df['position'] = np.minimum(df['index2'], df['tl2'])
        df['position'] = np.maximum(np.minimum(df['position'], df['tl2']), df['position'] - 3)
        df['position'] = df['position'].astype(int)
        df['old_position'] = df['old_position'].astype(int)
        df['group'] = df['group'].astype(int)

        #

        df['moved_fields'] = df['position'] - df['old_position']
        #col3.write(df[['NAVN', 'old_position','moved_fields','position']])
        del df['tl2']

        for i in range(0, df.shape[0]):
            st.write(df.iloc[i]['NAVN'])
            st.write('From group', df.iloc[i]['group'], 'moves', df.iloc[i]['moved_fields'], 'fields from', df.iloc[i]['old_position'], 'to', df.iloc[i]['position'])
            if df.iloc[i]['takes_lead'] == 0:
                st.write('refrains from leading')

            st.write(' ')


        st.header('2. EXHAUSTION CARDS')
        df['ECs'] = 0
        # df['played_card'] = 'kort 5'
        # df['played_card'][0:4] = 'kort 10'
        #col3.write('MOVED FIELDS')
        #for i in df.index.tolist():
        #    col3.write(df.loc[i, 'NAVN'], df.loc[i, 'moved_fields'])
        # df['played_card'] = np.random.randint(1,16, df.shape[0])

        df['played_card'] = df.played_card.str.extract(r'(\d+[.\d]*)').astype(int)
        df['noECs'] = np.floor((15 - df['played_card']) / 5)

        #col3.write(df[['NAVN', 'old_position', 'moved_fields', 'position']])
        #col3.write(track)

        df['noECs_bakke'] = df.apply(lambda row: tjek_bakke(row['old_position'], row['position'], track), axis=1)
        df['noECs_bakke'] = np.floor((15 - df['played_card']) / 10) * df['noECs_bakke']

        df['noECs'] = np.maximum(df['noECs_bakke'], df['noECs'])

        # assign trætkort
        liste = []
        for i in range(1, df['group'].max() + 1):
            print(i)
            liste.append(df[df.group == i].position.max() + 1000 * i)

        df['liste'] = df['position'] + 1000 * df['group']

        df.loc[df['liste'].isin(liste), ['ECs']] = df['noECs'] * df['takes_lead'] * df['method_takes_ECs']

        df['noECs_bakke'] = df['noECs_bakke'] * df['method_takes_ECs']
        df['ECs'] = np.maximum(df['noECs_bakke'], df['ECs'])

        #WRITE!!!
        for i in range(0, df.shape[0]):
            if df.iloc[i]['ECs'] > 1:

                st.write(':red[', df.iloc[i]['NAVN'], '] takes 2 exhaustion cards for playing card no 1-5 and taking the lead in the group')
            if df.iloc[i]['ECs'] == 1:
                if df.iloc[i]['noECs_bakke'] == 0:
                    st.write(':red[', df.iloc[i]['NAVN'], ']takes 1 exhaustion card for playing card no 6-10 and taking the lead in the group')
                if df.iloc[i]['noECs_bakke'] == 1:
                    st.write(':red[', df.iloc[i]['NAVN'], ']takes 1 exhaustion card for playing card no 1-5 on an ascent')

        #col3.write(df[['NAVN', 'old_position', 'moved_fields', 'position', 'noECs_bakke', 'ECs', 'noECs', 'method_takes_ECs']])

        #del df['liste']
        # gruppesplit
        st.header('3. GROUP SPLIT')
        df['vedhang'] = df.apply(lambda row: check_vedhang(row['moved_fields'], row['position'], track), axis=1)

        df = df.sort_values(by=['group', 'position'], ascending=[True, False])
        positions = df.sort_values(by=['group', 'position'], ascending=[True, False]).position.tolist()
        vedhang_positions = df.sort_values(by=['group', 'position'], ascending=[True, False]).vedhang.tolist()
        group_numbers = df.sort_values(by=['group', 'position'], ascending=[True, False]).group.tolist()

        split = 100

        old_groups = group_numbers * 1

        # vedhæng split
        for i in range(df.shape[0]):
            if group_numbers[i] > group_numbers[i - 1]:
                split = 100

            if positions[i] < split:
                if vedhang_positions[i] > 0:

                    split = positions[i] - vedhang_positions[i]
                    for j in range(i + 1, df.shape[0]):
                        if group_numbers[i] == group_numbers[j]:
                            if positions[j] < split + 1:
                                #st.write(df.iloc[i]['NAVN'], 'does not follow', df.iloc[i-1]['NAVN'])
                                for k in range(j, df.shape[0]):
                                    #st.write('k', k)
                                    group_numbers[k] = group_numbers[k] + 1

        #print('fladsplit')

        #for group in list(set(group_numbers)):
        #st.subheader('Split at top of ascent')
        group_diff = 0
        for i in range(df.shape[0] - 1):
         #       if group_numbers[i] == group:

          #      for i if group_numbers[i]


            if group_numbers[i] > old_groups[i]:
                if old_groups[i] == 1:
                    st.write(':red[', df.iloc[i]['NAVN'], ']moves from group', old_groups[i], ' to group', group_numbers[i], 'as his group get splitted per every', vedhang_positions[i], 'at the top of ascent')
                    group_diff = group_numbers[i] - old_groups[i]
                    previous_group = old_groups[i]

                if old_groups[i] > 1:
                    if group_numbers[i] - old_groups[i] == group_diff:
                        st.write(':red[', df.iloc[i]['NAVN'], ']moves from group', old_groups[i], ' to group',
                                 group_numbers[i], 'as the group in front of him splits')

                    else:
                        st.write(':red[', df.iloc[i]['NAVN'], ']moves from group', old_groups[i], ' to group',
                                 group_numbers[i], 'as the group he is in splits per every', vedhang_positions[i], 'on the top of ascent')

        for i in range(df.shape[0] - 1):
            print('i=', i)
            if group_numbers[i] == group_numbers[i + 1]:
                print('yrs')
                if positions[i] > 1 + positions[i + 1]:
                    if track[positions[i]] in ['^', 1, 2, 3, 4, 5, 6, 7, 8]:
                        st.write('Group', group_numbers[i], 'gets split on the ascent')
                        for j in range(i +1, df.shape[0] - 1):
                            if group_numbers[j] == group_numbers[i+1]:
                                st.write(df.iloc[i]['NAVN'], 'falls behind group', group_numbers[i+1])
                        for k in range(i + 1, df.shape[0]):
                            print('k', k)
                            group_numbers[k] = group_numbers[k] + 1

                    elif positions[i] > 2 + positions[i + 1]:
                        st.write('Group', group_numbers[i], 'gets split on the ascent')
                        for j in range(i + 1, df.shape[0] - 1):
                            if group_numbers[j] == group_numbers[i + 1]:
                                st.write(df.iloc[i+1]['NAVN'], 'gets dropped from group', group_numbers[i+1])

                        for k in range(i + 1, df.shape[0]):
                            print('k', k)
                            group_numbers[k] = group_numbers[k] + 1
                            print(group_numbers[k])

        # slipstream
        st.header('4. SLIPSTREAM')
        k = -100
        pos_before = positions

        for i in range(df.shape[0]):
            if group_numbers[i] > group_numbers[i - 1]:
                k = -100

            if i > k:

                if track[positions[i]] == '-' or track[positions[i]] == '_':
                    for j in range(i + 1, df.shape[0]):
                        if group_numbers[j] == group_numbers[i]:
                            positions[j] = int(positions[i] - np.floor((positions[i] - positions[j]) / 2))
                            k = j

        # man kan få slipstream bagfra
        for i in range(1, df.shape[0]):
            print(i)
            if positions[i] > positions[i - 1]:
                if track[positions[i]] == '-' or track[positions[i]] == '_':
                    for j in range(0, i):
                        if positions[i] > positions[j]:
                            positions[j] = int(positions[i] - np.floor((positions[i] - positions[j]) / 2))

        for i in range(1, df.shape[0]):
            if positions[i] > pos_before[i]:
                st.write(df.iloc[i]['NAVN'], 'moves from',pos_before[i] ,'to', positions[i],'by getting slipstream')


        old_groups = group_numbers * 1
        st.header('5. GROUP MERGE')


        for i in range(1, df.shape[0]):
            written = 0
            for l in range(0, i):
                if positions[i] >= positions[l]:
             #       print('to', l)

                    if group_numbers[i] > group_numbers[l]:
              #          print('tre')
                        group_numbers[i] = group_numbers[l]

                        for j in range(i + 1, df.shape[0]):
               #             print('fire')
                            group_numbers[j] = group_numbers[j] - 1
                            if written == 0:
                                st.write('group', group_numbers[j]+1, 'gets merged into group', group_numbers[j])
                                written = 1
        sprint_groups = []

        for i in range(df.shape[0]):
            writtenspr = 0
            if positions[i] > track.find('F')-1:
                if writtenspr == 0:

                    writtenspr = 1
                sprint_groups.append(group_numbers[i])


                #col3.write('group' + str(group_numbers[i]) + 'sprints')

        sprint_groups = list(set(sprint_groups))



        # overføre til datasæt
        df['position'] = positions
        df['group'] = group_numbers
        df = df.sort_values(by='index2', ascending=True)


        if sprint_groups:
            st.header(':green[6. SPRINT]')
            for group in sprint_groups:

                df.loc[df['group'] == group, ['prel_time']] = (track.find('F') - df['old_position']) / (
                            df['position'] - df['old_position']) * 100 + df['prel_time']

                df.loc[df['group'] == group, ['prel_time']] = df[df['group'] == group]['prel_time'].min()



        df.loc[~df['group'].isin(sprint_groups), ['prel_time']] = df['prel_time'] + 100

        df['time'] = df['prel_time'] - df['prel_time'].min()
        #st.write(df[['NAVN', 'group', 'prel_time', 'position', 'old_position', 'time']])

        df['old_position'] = df['position']
        df['group'] = df['group'].astype(int)

    return df, sprint_groups

def transfer_ECs(df, dict):
    sdf = df[df.method_takes_ECs == 1]
    for rider in sdf.NAVN.tolist():
        ECs = int(sdf[sdf.NAVN == rider].ECs)
        #st.write(rider + ':' + str(ECs) + 'ECs')
        for i in range(ECs):
            dict[rider]['cards'].insert(0, ['EC 15',2,2])
            #
            #st.write('done')

    #df['ECs'] = 0

    return dict


def colour_track(track):
    stigning = 0
    track2 = track
    i = 0

    while i < 20:
        # print('s2',stigning)
        # print(track2)
        # print(track2[stigning:])

        if track2[stigning:].find('^') == -1:
            break

        stigning = track2[stigning:].find('^') + stigning
        # print('stigning', stigning)

        track2 = track2[0:stigning] + ':red[' + track2[stigning:]
        # print(track2)

        ned_igen = track2[stigning:].find('_')
        if ned_igen == -1:
            ned_igen = 1000

        ned_igen2 = track2[stigning:].find('-')
        if ned_igen2 == -1:
            ned_igen2 = 1000

        ned_igen = min(ned_igen, ned_igen2)

        if ned_igen == 1000:
            i = 21

        # print(ned_igen)

        track2 = track2[0:stigning + ned_igen] + ']' + track2[stigning + ned_igen:]
        stigning = stigning + ned_igen + 2
        # print('s',stigning)

    nedad = 0

    i = 0
    # blue
    while i < 20:
        print('s2', stigning)
        print(track2)
        # print(track2[stigning:])

        if track2[nedad:].find('_') == -1:
            break

        nedad = track2[nedad:].find('_') + nedad
        # print('stigning', stigning)

        track2 = track2[0:nedad] + ':blue[' + track2[nedad:]
        # print(track2)

        ned_igen = track2[nedad:].find('-')
        if ned_igen == -1:
            ned_igen = 1000

        ned_igen2 = track2[nedad:].find('^')
        if ned_igen2 == -1:
            ned_igen2 = 1000

        ned_igen = min(ned_igen, ned_igen2)

        if ned_igen == 1000:
            i = 21

        # print(ned_igen)

        track2 = track2[0:nedad + ned_igen] + ']' + track2[nedad + ned_igen:]
        nedad = nedad + ned_igen + 2
        # print('s',stigning)

    if track2.find('F')>-1:

        track2 = track2[0:track2.find('F')] + ':green[F]' + track2[track2.find('F')+1:]
    # blue

    return track2


def move_rider(position, played_card, track):
    if track[position] == '_':

        new_position = position + max(5, played_card[1])
    elif track[position] == '^':
        new_position = position + played_card[2]
    elif '^' in track[position:position+played_card[1]]:
        new_position = position + played_card[2]
    elif track[position-1] == '^':
        new_position = position + played_card[2]
    elif track[position] == 'F':
        new_position = position + 7
    else:

        new_position = position + played_card[1]

    moved_fields = new_position-position
    return new_position, moved_fields

def transfer_positions(dict,df):
    #df = df.sort_values(by='index', ascending=True)
    i = 0
    for rider in dict:
        df.loc[df['NAVN'] == rider, 'position'] = dict[rider]['position']
        df.loc[df['NAVN'] == rider, 'moved_fields'] = dict[rider]['moved_fields']
        df.loc[df['NAVN'] == rider, 'played_card'] = dict[rider]['played_card'][0]
        df.loc[df['NAVN'] == rider, 'takes_lead'] = dict[rider]['takes_lead']
        #st.write(dict[rider]['played_card'][0])
        #df[df['NAVN' == rider]]['position'] = dict[rider]['position']
        #i = 1 + i
    return(df)

def rankings_from_dict_to_df(dict,df):
    #df = df.sort_values(by='index', ascending=True)

    for rider in dict:
        df.loc[df['NAVN'] == rider, 'ranking'] = dict[rider]['ranking']
        # df[df['NAVN' == rider]]['position'] = dict[rider]['position']
        # i = 1 + i
    return (df)
        #i = 1 + i


def from_dict_to_df(dict,df):
    #df = df.sort_values(by='index', ascending=True)
    i = 0
    for rider in df['NAVN'].tolist():
        dict[rider]['position'] = df[df['NAVN'] == rider]['position'].tolist()[0]
        dict[rider]['played_card']=0
        dict[rider]['group'] = df[df['NAVN']==rider]['group'].tolist()[0]

        #df[df['NAVN' == rider]]['position'] = dict[rider]['position']
        #i = 1 + i
    return(dict)


def takes_lead(rider, df):

    takes_lead = 0
    team = df[df['NAVN'] == rider]['team'].tolist()[0]
    group = df[df['NAVN'] == rider]['group'].tolist()[0]
    sdf = df[df['group'] == group]
    ratio = sdf[sdf.team == team].shape[0] / sdf.shape[0]
    print(ratio)
    ratio = ratio + random.randint(0, 20) / 100
    ratio = ratio - random.randint(0, 20) / 100
    print(ratio)
    if ratio > 0.33:
        takes_lead = 1

    return takes_lead


def nyehold(df):
    #global cards
    df = df.head(66)
    rdf = df.sample(9)
    #rdf = df[0:9]
    rdf['team'] = 'V'
    rdf['team'][0:3] = 'Me'
    rdf['team'][3:6] = 'Comp1'
    rdf['team'][6:9] = 'Comp2'
    rdf['method'] = 'V'
    rdf['method'][0:3] = 'Human'
    rdf['method'][3:6] = 'Comp1'
    rdf['method'][6:9] = 'Comp1'
    rdf['method_takes_ECs'] = 1
    rdf['method_takes_ECs'][3:9] = 0
    rdf['takes_lead'] = 1
    rdf['played_card'] = ''
    rdf['moved_fields'] = 0
    rdf['position'] = 0
    rdf['old_position'] = 0
    rdf['index2'] = range(0,9)
    rdf['noECs'] = 0
    rdf['group'] = 1
    rdf['index'] = range(1,10)
    rdf['ECs'] = 0
    rdf['prel_time'] = 0

    riders = rdf.NAVN.tolist()


    cards = {}
    i = -1
    for rider in riders:
        i = i + 1
        cards[rider] = {}
        cards[rider]['position'] = 0
        cards[rider]['cards'] = []
        cards[rider]['discarded'] = []
        cards[rider]['group'] = 1
        cards[rider]['played_card'] = 0
        cards[rider]['moved_fields'] = 0
        cards[rider]['sprint'] = rdf.iloc[i]['SPRINT']
        cards[rider]['sprint_points'] = 0
        cards[rider]['ranking'] = 0


        for j in range(15):
            cards[rider]['cards'].append(['kort: ' + str(j + 1), int(rdf.iloc[i, 17 + j]), int(rdf.iloc[i, 32 + j])])

        random.shuffle(cards[rider]['cards'])
        #cards['select']={}

        gcdf = rdf.copy()
        gcdf['prel_time'] = 1000

    return cards, rdf, gcdf, riders


#hvis alt går galt
#st.session_state.cards, st.session_state.rdf, st.session_state.riders2 = nyehold(pd.read_csv('FRData -FRData.csv'))



col1, col2, col3, col4 = st.columns([1,1,1,1], gap='small')

col1.title('Actions')
col1.write('------------')
col2.title('Situation')
col2.write('------------')
col3.title('Game actions')
col3.write('------------')
col4.title('The Riders')
#col4.subheader('and their stats')
col4.write('------------')


    #rdf = rdf.sort_values(by='position', ascending=False)
#col3.write(st.session_state.rdf)

#col3.write(st.session_state.cards)

##################
track = '^^1---------^^^^3__------------^^^^^^^^^4------^^^^^2_----^^1-----FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'
track2 = colour_track(track[0:track.find('F')+1])
#human_chooses_cards = False
computer_chooses_cards = False
ready_for_calculate = False

with col3:
    st.write('full track' + track2)
    #st.write('ryttere tilbage', len(st.session_state.riders))



#col2.write(st.session_state.rdf[['NAVN', 'team', 'position', 'group']])

#else:
#    ryttervalg = None
#ryttervalg = st.radio("Who to pick first", (riders[0], riders[1], riders[2]))
# if col1.button('start_tur'):
#    st.session_state.ryttervalg = col1.selectbox("Who to pick first", options = [
 #   st.session_state.riders[0], st.session_state.riders[1], st.session_state.riders[2]], index=0)
####1####

#def human_chooses_cards(cards, riders):
if len(st.session_state.riders) > 0:
#if st.session_state.human_chooses_cards ==9:


    with col1:
        #goto2 = False
        #st.write('ryttere tilbage', len(st.session_state.riders))
        #st.write(st.session_state.human_chooses_cards)
        #if len(st.session_state.riders) == 3:
        #if st.session_state.human_chooses_cards == 9:

        #mi = st.empty()
        keystring = str(len(st.session_state.riders)) + '1'
        st.session_state.ryttervalg = col1.radio("Who to pick", options= st.session_state.riders, index=0)
        checkbx = st.checkbox('choose', key=keystring, value=False)

        if checkbx:
            col1.write(colour_track(track[st.session_state.cards[st.session_state.ryttervalg]["position"]:
                                          st.session_state.cards[st.session_state.ryttervalg]["position"] + 10]))
            #st.session_state.ryttervalg = col1.number_input('?')
            #st.session_state.human_chooses_cards = 8
            #if select11:
                #st.session_state.human_chooses_cards == 8:
                #human_chooses_cards = False
            #select12 = False

            keystring2 = str(len(st.session_state.riders)) + '2'
            st.session_state.cards[st.session_state.ryttervalg]['played_card'] = col1.radio('hvilket kort?',(st.session_state.cards[st.session_state.ryttervalg]['cards'][0], st.session_state.cards[st.session_state.ryttervalg]['cards'][1], st.session_state.cards[st.session_state.ryttervalg]['cards'][2], st.session_state.cards[st.session_state.ryttervalg]['cards'][3], ['EC-Xtra 15', 2, 2]),  key=keystring2)
            #select12 = st.button('choose card', key=1212)  # st.session_state.ryttervalg = col1.number_input('?')


            checkbx2 = st.checkbox('choose card', value = False)
            if checkbx2:

                keystring3 = str(len(st.session_state.riders)) + '3'
                checkbx2 = False
                st.session_state.cards[st.session_state.ryttervalg]['takes_lead'] = col1.radio('takes the lead', (True, False), key=keystring3)

                checkbx3 = st.checkbox('confirm', value=False)

                if checkbx3:

                    checkbx = False
                    st.session_state.cards[st.session_state.ryttervalg]['takes_lead'] = int(st.session_state.cards[st.session_state.ryttervalg]['takes_lead'])
                #select111 = False
                    col3.write(st.session_state.ryttervalg)
                    col3.write(st.session_state.cards[st.session_state.ryttervalg]["position"])
                    checkbx = False
                    # mi.checkbox('choose', value=False, key=1111)
                    # if select12:
                    #            if st.session_state.cards[st.session_state.ryttervalg]['played_card']:
                    played_card = st.session_state.cards[st.session_state.ryttervalg]['played_card']
                    # st.write('played_card', type(st.session_state.cards[st.session_state.ryttervalg]['played_card']), st.session_state.cards[st.session_state.ryttervalg]['played_card'][3])

                    # st.session_state.rdf.loc[st.session_state.rdf['NAVN'] == st.session_state.ryttervalg, 'position'] = move_rider(st.session_state.rdf[[st.session_state.ryttervalg]['position']], played_card, track)
                    st.session_state.cards[st.session_state.ryttervalg]['position'], \
                    st.session_state.cards[st.session_state.ryttervalg]['moved_fields'] = move_rider(
                        st.session_state.cards[st.session_state.ryttervalg]['position'], played_card, track)

                    for card in st.session_state.cards[st.session_state.ryttervalg]['cards'][0:4]:
                        st.session_state.cards[st.session_state.ryttervalg]['discarded'].append(card)
                    if played_card[0] != 'EC-Xtra 15':
                        st.session_state.cards[st.session_state.ryttervalg]['discarded'].remove(played_card)
                    del st.session_state.cards[st.session_state.ryttervalg]['cards'][0:4]
                    col3.write('ny position:')
                    col3.write(st.session_state.cards[st.session_state.ryttervalg]['position'])

                    #st.write('kort tilbage' + str(len(st.session_state.cards[st.session_state.ryttervalg]['cards'])))
                    if len(st.session_state.cards[st.session_state.ryttervalg]['cards']) < 4:
                        st.write('new cards')
                        random.shuffle(st.session_state.cards[st.session_state.ryttervalg]['discarded'])
                        for card in st.session_state.cards[st.session_state.ryttervalg]['discarded']:
                            st.session_state.cards[st.session_state.ryttervalg]['cards'].append(card)

                        st.session_state.cards[st.session_state.ryttervalg]['discarded'] = []

                        # if select111:
                    st.session_state.riders.remove(st.session_state.ryttervalg)
                    if st.button('next rider'):


                        checkbx3 = False


#st.session_state.riders = []

if col3.button('make new teams'):
    st.session_state.cards, st.session_state.rdf, st.session_state.gcdf, st.session_state.riders2 = nyehold(pd.read_csv('FRData -FRData.csv', encoding='utf-8'))
    #col2.write('riders:')
    #col2.write(st.session_state.riders)
    #col2.write(st.session_state.cards)
    st.session_state['placering'] = 0
    st.session_state.riders = [st.session_state.riders2[0], st.session_state.riders2[1],
                               st.session_state.riders2[2]]
    #st.session_state.riders = []

    st.session_state.human_chooses_cards = 9

    with col4:
        for team in st.session_state.rdf['team'].unique():
            st.title(':blue[' + team + ']')
            for rider in st.session_state.rdf[st.session_state.rdf.team == team]['NAVN'].unique():
                st.markdown(':green[' + rider + ']')
                st.write('Flat:' + str(int(st.session_state.rdf[st.session_state.rdf.NAVN == rider]['FLAD'])) + '  Uphill:' + str(int(st.session_state.rdf[st.session_state.rdf.NAVN == rider]['BJERG'])) + '  Sprint:' + str(int(st.session_state.rdf[st.session_state.rdf.NAVN == rider]['SPRINT'])))
                #st.caption()
                #st.caption('Sprint:' + str(int(st.session_state.rdf[st.session_state.rdf.NAVN == rider]['SPRINT'])))
                flatlist = []
                for i in range(1, 16):
                    # field = 'FLAD'+str(i)
                    flatlist.append(int(st.session_state.rdf[st.session_state.rdf.NAVN == rider]['FLAD' + str(i)].tolist()[0]))

                j = 0
                flatstr = ''
                for i in flatlist:
                    flatstr = flatstr + str(i)
                    j = 1 + j
                    if j % 5 == 0:
                        flatstr = flatstr + '|'

                st.caption('Flat:' + flatstr)



                uplist = []
                for i in range(1, 16):
                    # field = 'BJERG'+str(i)
                    uplist.append(int(st.session_state.rdf[st.session_state.rdf.NAVN == rider]['BJERG' + str(i)].tolist()[0]))

                j = 0
                flatstr = ''
                for i in uplist:
                    flatstr = flatstr + str(i)
                    j = 1 + j
                    if j % 5 == 0:
                        flatstr = flatstr + '|'

                st.caption('Uphill:' + flatstr)

                #st.write('Uphill:', flatlist)
    #human_chooses_cards(st.session_state.cards, st.session_state.riders)

#if st.session_state.computer_chooses_cards:

with col1:

    #col1.write(st.session_state.riders)
#if rytter2:
    if len(st.session_state.riders) == 0:
        begin_computer = col1.button('computer move')

        if begin_computer:
            st.session_state.computer_chooses_cards = False
            for rider in st.session_state.cards:

                if st.session_state.cards[rider]['played_card'] == 0:
                    if len(st.session_state.cards[rider]['cards']) == 0:
                        st.session_state.cards[rider]['cards'].append(['EC15',2,2])
                    st.session_state.cards[rider]['position'], st.session_state.cards[rider]['moved_fields'] = move_rider(st.session_state.cards[rider]['position'], st.session_state.cards[rider]['cards'][0], track)
                    st.write(rider, 'played', st.session_state.cards[rider]['cards'][0][0], st.session_state.cards[rider]['cards'][0][1], st.session_state.cards[rider]['cards'][0][2])
                    #st.write('position', st.session_state.cards[rider]['position'])
                    st.session_state.cards[rider]['played_card'] = st.session_state.cards[rider]['cards'][0]
                    st.session_state.cards[rider]['takes_lead'] = takes_lead(rider, st.session_state.rdf)
                    #st.write(st.session_state.cards[rider]['played_card'])
                    del st.session_state.cards[rider]['cards'][0]
            st.session_state.ready_for_calculate = True


if st.session_state.ready_for_calculate:
    if col1.button('do_everything'):
        #col1.write('do_everything')
        st.session_state.rdf = transfer_positions(st.session_state.cards, st.session_state.rdf)
        #st.write(st.session_state.rdf.group.max())
        st.session_state.rdf, sprint_groups = do_everything(st.session_state.rdf)


        st.session_state.cards = transfer_ECs(st.session_state.rdf, st.session_state.cards)
        st.session_state.cards = from_dict_to_df(st.session_state.cards, st.session_state.rdf)

        #st.session_state.riders = [st.session_state.riders2[0], st.session_state.riders2[1],
    #                               st.session_state.riders2[2]]

        st.session_state.riders =st.session_state.rdf[st.session_state.rdf.team == 'Me']['NAVN'].tolist()

        if sprint_groups:


            for sprint_group in sprint_groups:
                st.session_state.cards = sprint(sprint_group, st.session_state.cards, st.session_state.rdf)

                st.session_state.rdf = rankings_from_dict_to_df(st.session_state.cards, st.session_state.rdf)
                st.session_state.rdf = st.session_state.rdf.sort_values(by='ranking', ascending=True)

                  #del st   .session_state.cards[rider]
                    #st.session_state.riders.remove(rider)
            st.session_state.riders =st.session_state.rdf[st.session_state.rdf.team == 'Me']['NAVN'].tolist()


            riders_left = []
            for rider in st.session_state.cards:

                riders_left.append(rider)

            for rider in riders_left:
                if st.session_state.cards[rider]['ranking'] > 0:
                    #col3.write(rider + 'gets removed')
                    del st.session_state.cards[rider]
                    if rider in st.session_state.riders:
                        st.session_state.riders.remove(rider)

                    st.session_state.rdf.loc[st.session_state.rdf['NAVN'] == rider,
                        'played_card'] = 'Finished 15'
                    st.session_state.gcdf.loc[st.session_state.gcdf['NAVN'] == rider,
                    'time'] = int(st.session_state.rdf.loc[st.session_state.rdf['NAVN'] == rider]['time'])
                    st.session_state.gcdf.loc[st.session_state.gcdf['NAVN'] == rider,
                    'prel_time'] = int(st.session_state.rdf.loc[st.session_state.rdf['NAVN'] == rider]['prel_time'])

                    st.session_state.gcdf.loc[st.session_state.gcdf['NAVN'] == rider,
                    'ranking'] = int(st.session_state.rdf.loc[st.session_state.rdf['NAVN'] == rider]['ranking'])

                    st.session_state.rdf.loc[st.session_state.rdf['NAVN'] == rider,
                    'played_card'] = 'Finished 15'

                    st.session_state.rdf = st.session_state.rdf.drop(st.session_state.rdf[st.session_state.rdf['NAVN'] == rider].index)

            # position = 100+position, played_card = 15
            #st.write('rdf:')



            #st.write('gcdf:')
            st.session_state.gcdf['time'] = st.session_state.gcdf['prel_time'] - st.session_state.gcdf['prel_time'].min()

            #st.write(st.session_state.gcdf[
                #         ['NAVN', 'position', 'group', 'ECs', 'played_card',
                 #         'prel_time', 'time', 'ranking']])

           # col3.write(st.session_state.cards)

            col2.header(':green[Results]')
            st.session_state.gcdf = st.session_state.gcdf.sort_values(by='ranking', ascending = True)

            for rider in st.session_state.gcdf[st.session_state.gcdf.ranking > 0].NAVN.tolist():
                col2.write(str(int(st.session_state.gcdf.loc[st.session_state.gcdf['NAVN'] == rider][
                                       'ranking'])) + '. ' + rider + '(' + str(st.session_state.gcdf.loc[st.session_state.gcdf['NAVN'] == rider]['team'].tolist()[0])
                           + '): ' + str(convert_to_seconds_plain(
                        int(st.session_state.gcdf.loc[st.session_state.gcdf['NAVN'] == rider]['time']))))

#                if st.session_state.gcdf.loc[st.session_state.gcdf['NAVN'] == rider]['team'] == 'Me':
#                    col2.write(":green[", str(int(st.session_state.gcdf.loc[st.session_state.gcdf['NAVN'] == rider][
#                                       'ranking'])) + '. ' + rider + ': ' + str(
#                    convert_to_seconds_plain(int(st.session_state.gcdf.loc[st.session_state.gcdf['NAVN'] == rider]['time']))), "]")
#                else:
#                    col2.write(str(int(st.session_state.gcdf.loc[st.session_state.gcdf['NAVN'] == rider][
#                                                      'ranking'])) + '. ' + rider + ': ' + str(
#                        convert_to_seconds_plain(
 #                           int(st.session_state.gcdf.loc[st.session_state.gcdf['NAVN'] == rider]['time']))))

            if st.session_state.rdf.shape[0] == 0:
                col2.header('Race is over')

        #st.session_state.human_chooses_cards = True


        if col1.button('start new round'):
            for rider in [st.session_state.riders2[0], st.session_state.riders2[1], st.session_state.riders2[2]]:
                st.write('start new round')
            st.session_state.ready_for_calculate = False

        #human_chooses_cards()



    #trætkort





#with col2:
    #st.write(st.session_state.cards)

#Write Groups in column 2

if col3.button('reshuffler'):
#reshuffler = col3.button([st.session_state.riders2[0], st.session_state.riders2[1],
                                   #st.session_state.riders2[2]]
    for rider in [st.session_state.riders2[0], st.session_state.riders2[1],
                                   st.session_state.riders2[2]]:

        col3.write(rider)
        random.shuffle(st.session_state.cards[rider]['discarded'])
        for card in st.session_state.cards[rider]['discarded']:
            st.session_state.cards[rider]['cards'].append(card)
        st.session_state.cards[rider]['discarded'] = []

with col2:
    if st.session_state.rdf.shape[0] > 0:
        max_position = st.session_state.rdf['position'].max()
        #st.write('max_gruppe:', st.session_state.rdf['group'].max(), type(st.session_state.rdf['group'].max()))

        for i in range(st.session_state.rdf['group'].min(),st.session_state.rdf['group'].max()+1):
            time = 17*(max_position - st.session_state.rdf[st.session_state.rdf['group'] == i]['position'].max())
            time_string = convert_to_seconds(time)
            max_position = st.session_state.rdf['position'].max()
            km_left = get_length(track[max_position::])
            if i == 1:
                st.header(str(km_left) + 'km left')
                st.header('Group ' + str(i) + ' (' + time_string + ')')
            else:
                st.header('Group ' + str(i) + ' (' + time_string + ')')

            minimum = int(st.session_state.rdf[st.session_state.rdf['group'] == i]['position'].min())

            st.markdown(str(minimum) + ':   ' + colour_track(track[minimum:minimum+10]))
            st.text('')
            riders = st.session_state.rdf[st.session_state.rdf['group'] == i].sort_values(by='position', ascending=False)['NAVN'].tolist()
            positions = st.session_state.rdf[st.session_state.rdf['group'] == i].sort_values(by='position', ascending=False)['position'].tolist()
            ECs = st.session_state.rdf[st.session_state.rdf['group'] == i].sort_values(by='position', ascending=False)['ECs'].tolist()
            takes_lead = st.session_state.rdf[st.session_state.rdf['group'] == i].sort_values(by='position', ascending=False)[
                'takes_lead'].tolist()
            teams = \
            st.session_state.rdf[st.session_state.rdf['group'] == i].sort_values(by='position', ascending=False)[
                'team'].tolist()

            for i in range(len(riders)):
                if ECs[i] > 0:

                    st.write(riders[i] + ' . ' + str(positions[i]) + ' (' + teams[i] + ')' + ' :red[takes ' + str(int(ECs[i])) + ' ECs]' )

                else:
                    st.caption(riders[i] + ' . ' + str(positions[i]) + ' (' + teams[i] + ')')
                if takes_lead[i] == 0:
                    st.caption(':blue[refrains from leading]')


    #st.write(st.session_state.rdf[['NAVN', 'position', 'group', 'ECs','played_card','takes_lead','noECs', 'method_takes_ECs', 'prel_time', 'time', 'ranking']])







