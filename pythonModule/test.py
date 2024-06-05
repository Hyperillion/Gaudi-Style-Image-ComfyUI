result = [{'Confidence': 18.08, 'Label': 'sexual_femaleUnderwear'}, {'Confidence': 17.82, 'Label': 'suggestiveContent_sexhint'}]
print(type(result))

if any(i['Confidence'] >= 20 for i in result):
    print('fail')
else:
    print('pass')