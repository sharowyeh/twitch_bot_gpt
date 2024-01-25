from gptchat import GPTChat

def test_split_text():
    text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis porttitor lectus ac ex vulputate, eu suscipit enim vehicula. Donec non gravida ex. Vivamus scelerisque ultrices augue, quis rhoncus leo mattis nec.\
Integer hendrerit malesuada metus, eu dictum nibh fermentum nec. Nullam consectetur, metus ac ultricies fringilla, tellus libero pellentesque ipsum, ut pulvinar enim augue vitae urna. Quisque semper eleifend leo, eu scelerisque odio suscipit vel.\
Praesent vehicula enim sit amet est faucibus laoreet. Donec et bibendum massa. Nam at magna velit. Nunc id erat blandit, dictum velit sed, vestibulum orci.\
Sed suscipit auctor nunc ut interdum. Etiam vel justo vel augue fermentum dictum. In sagittis dapibus ligula ac lobortis. Duis blandit quis ex non aliquam.\
Donec sed augue suscipit, sollicitudin est sit amet, consequat quam. Nulla sollicitudin turpis id nunc maximus bibendum. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae;\
Sed condimentum risus nec urna feugiat aliquet. Nullam lobortis sapien vel urna feugiat, eget rutrum risus convallis. Donec commodo elit eget elit congue, id convallis ex laoreet. Nulla facilisi.\
Vivamus at lacus tincidunt, aliquet tellus quis, accumsan tellus. Vestibulum lacinia erat at tortor rutrum sollicitudin. Sed bibendum justo a aliquet scelerisque. Nulla facilisi.\
Sed semper ultricies dolor, at efficitur sapien hendrerit ac."
    gptchat = GPTChat()
    chunks = gptchat.splitText(text)
    for c in chunks:
        print(f"{c}\n")

test_split_text()