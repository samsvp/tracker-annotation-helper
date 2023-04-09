function loadData() {
    fetch('/load_data')
        .then(res => res.json()
            .then(data => {
                for (frame in data) {
                    squares[frame] = data[frame].map(s => {
                        return new Square(s.bb_left, s.bb_top,
                            s.bb_width, s.bb_height,
                            s.id)
                    });
                }
            })
            .catch(err => console.log(err)))
        .catch(err => console.log(err));
}


function getFrameData() {
    fetch('/get_current_frame')
        .then(res => res.json()
            .then(json => {
                frame = json.frame;
                document.getElementById("curr-frame").innerHTML = frame;
                if (!(frame in squares)) {
                    console.log(frame);
                    squares[frame] = [];
                }
                drawSquares();
            })
            .catch(err => console.log(err)))
        .catch(err => console.log(err));
}


function loadImage(nextOrPrev) {
    fetch(`/${nextOrPrev}_image`)
        .then(
            res => res.blob()
                .then(imageBlob => {
                    const imageUrl = URL.createObjectURL(imageBlob);
                    img.src = imageUrl;
                    img.onload = getFrameData;
                })
                .catch(err => console.log(err)))
        .catch(err => console.log(err))
}


function loadSelectedImage(frame) {
    fetch(`/get_image`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ frame: frame })
    })
        .then(
            res => res.blob()
                .then(imageBlob => {
                    const imageUrl = URL.createObjectURL(imageBlob);
                    img.src = imageUrl;
                    img.onload = getFrameData;
                })
                .catch(err => console.log(err)))
        .catch(err => console.log(err))
}


function exportToMOT(filename) {
    let result = "";

    Object.keys(squares).forEach(frame => squares[frame].forEach(square => {
        const id = square.number;
        const x = square.x;
        const y = square.y;
        const w = square.width;
        const h = square.height;

        result += `${frame}, ${id}, ${x}, ${y}, ${w}, ${h}, -1, -1, -1, -1\n`;
    }));

    fetch('/save_square', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            squares: result
        })
    })
        .then(response => response.json()
            .then(data => {
                console.log(data);
                alert(data.msg)
            })
            .catch(error => console.error(error)))
        .catch(error => console.error(error));
}


function drawSquares() {
    if (squares[frame].length != 0) {
        squares[frame].forEach((square, i) => square.draw(canvas, ctx, img, i == 0));
    } else {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);
    }
}


function promptInt(message) {
    let number;
    while (number = prompt(message)) {
        if (isNaN(number)) {
            alert("Not a number");
        } else {
            break;
        }
    }
    return parseInt(number);
}