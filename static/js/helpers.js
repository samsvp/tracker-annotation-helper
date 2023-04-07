function getFrameData() {
    fetch('/get_current_frame_data')
        .then(res => res.json()
            .then(json => {
                frame = json.frame;
                if (!(frame in squares)) {
                    squares[frame] = json.squares.map(
                        s => {
                            return new Square(s.bb_left, s.bb_top, 
                                s.bb_width, s.bb_height,
                                s.id)
                        });
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


function exportToMOT(filename) {
    let result = "";

    squares[frame].forEach(square => {
        const id = square.number;
        const x = square.x;
        const y = square.y;
        const w = square.width;
        const h = square.height;

        result += `${frame+1}, ${id}, ${x}, ${y}, ${w}, ${h}, -1, -1, -1, -1\n`;
    })

    fetch('/save_square', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            squares: result,
            filename: filename
        })
    })
        .then(response => response.json()
            .then(data => console.log(data))
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