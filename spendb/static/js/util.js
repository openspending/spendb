

// https://stackoverflow.com/questions/1916218/find-the-longest-common-starting-substring-in-a-set-of-strings
function longestCommonStart(array){
    var A = array.concat().sort(), 
    a1 = A[0], a2 = A[A.length-1], L = a1.length, i = 0;
    while(i < L && a1.charAt(i) === a2.charAt(i)) i++;
    return a1.substring(0, i);
}

// https://stackoverflow.com/questions/1026069/capitalize-the-first-letter-of-string-in-javascript
function cleanLabel(text) {
    var ws = ' ',
        pieces = text.replace(/[\W_]/g, ws).split(ws);
    for ( var i = 0; i < pieces.length; i++ )
    {
        var j = pieces[i].charAt(0).toUpperCase();
        pieces[i] = j + pieces[i].substr(1);
    }
    return pieces.join(ws).replace(/\s+/g, ws).trim();
}
