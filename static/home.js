class Block {

    constructor(element, time) {
        this.element = element;
        this.time = time;
        this.selected = false;
        Block.all.push(this);
        Block.lookup[time] = this;
    }

    select() {
        this.selected = true;
        this.element.classList.add("selected");
    }

    deselect() {
        this.selected = false;
        this.element.classList.remove("selected");
    }

    toggle() {
        if (this.selected) this.deselect();
        else this.select();
    }

    setActivity(activity) {
        this.element.getElementsByClassName("activity")[0].innerHTML = activity.name;
        this.element.style.backgroundColor = color(activity.color);
        console.log(color(activity.color));
    }

}

Block.all = [];
Block.lookup = {};
Block.all.selected = function() {
    let selected = [];
    for (let i = 0; i < Block.all.length; i++)
        if (Block.all[i].selected)
            selected.push(Block.all[i]);
    return selected;
};

function color(value) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(value);
    return ("rgba(" + parseInt(result[1], 16) +
        ", " + parseInt(result[2], 16) +
        ", " + parseInt(result[3], 16) +
        ", " + 0.2 + ")");
}

class BlockSelection {

    constructor(element) {
        this.element = element;
    }

    update() {
        while (this.element.lastChild)
            this.element.removeChild(this.element.lastChild);
        for (let block of Block.all) {
            if (block.selected) {
                let mini = document.createElement("div");
                mini.classList.add("mini");
                mini.innerHTML = block.time;
                this.element.appendChild(mini);
            }
        }
    }

    clear(except) {
        for (let block of Block.all)
            if (block != except)
                block.deselect();
    }

}

const SHIFT = [16];
const CONTROL = [17, 91];

class BlockManager {

    constructor() {
        this.blocks = [];
        this.selection = new BlockSelection(document.getElementById("selection"));
        this.last = Block.all[0];
        this.modifiers = {shift: false, control: false};
        this.bind();
    }

    bind() {
        let that = this;
        document.addEventListener("keydown", function(e) {
            if (SHIFT.indexOf(e.keyCode) > -1) that.modifiers.shift = true;
            if (CONTROL.indexOf(e.keyCode) > -1) that.modifiers.control = true;
        });
        document.addEventListener("keyup", function(e) {
            if (SHIFT.indexOf(e.keyCode) > -1) that.modifiers.shift = false;
            if (CONTROL.indexOf(e.keyCode) > -1) that.modifiers.control = false;
        });
        for (let block of this.blocks) {
            block.element.addEventListener("click", function(e) {
                if (that.modifiers.shift) {
                    let start = Block.all.indexOf(block);
                    let end = Block.all.indexOf(that.last);
                    let increment = Math.sign(end - start);
                    for (let i = start; i != end; i += increment) {
                        if (!Block.all[i].selected) Block.all[i].select();
                        else break;
                    }
                } else {
                    if (!that.modifiers.control) {
                        that.selection.clear(block);
                    }
                    block.toggle();
                }
                that.last = block;
                that.selection.update();
            });
        }
    }

    getBlocks() {
        api({"command": "get-blocks"}, function(result) {
            for (let i = 0; i < result.blocks.length; i++) {
                let data = result.blocks[i];
                let block = Block.lookup[data.time];
                block.setActivity(data.activity);
            }
        });
    }

    setBlocks() {
        let activity = document.getElementById("activity").value.toLowerCase();
        let selection = Block.all.selected().map(function(x) { return x.time; });
        let that = this;
        api({"command": "set-blocks", "activity": activity, "blocks": selection}, function(result) {
            that.getBlocks();
        })
    }

}

function api(data, callback) {
    let request = new XMLHttpRequest();
    request.open("POST", "/api/");
    request.setRequestHeader("Content-Type", "application/json");
    request.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200)
            callback(JSON.parse(this.responseText));
    };
    request.send(JSON.stringify(data));
}

window.onload = function() {

    let manager = new BlockManager();

    let blocksElement = document.getElementById("blocks");
    for (let h = 0; h < 24; h++) {
        let row = document.createElement("tr");
        for (let m = 0; m < 6; m++) {
            let cell = document.createElement("td");
            let time = h + ":" + m + "0";
            cell.classList.add("block");
            cell.classList.add("noselect");
            cell.innerHTML = "<span class='time'>" + h + ":" + m + "0</span><br><span class='activity'></span>";
            manager.blocks.push(new Block(cell, time));
            row.appendChild(cell);
        }
        blocksElement.appendChild(row);
    }

    let editorElement = document.getElementById("editor");
    editorElement.style.left = blocksElement.getBoundingClientRect().right + 20;

    let activityElement = document.getElementById("activity");
    let saveElement = document.getElementById("save");
    activityElement.addEventListener("input", function() {
        saveElement.disabled = activityElement.value.trim() == "";
    });
    saveElement.addEventListener("click", function() {
        manager.setBlocks();
    });

    manager.bind();
    manager.getBlocks();

};
