class Block {

    constructor(element) {
        this.element = element;
        this.time = element.innerHTML.trim();
        this.sort = element.sort;
        this.selected = false;
        Block.all.push(this);
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

}

Block.all = [];

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

    clear() {
        for (let block of Block.all)
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
                } else if (!that.modifiers.control) {
                    that.selection.clear();
                }
                block.select();
                that.last = block;
                that.selection.update();
            });
        }
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

    let blockElements = document.getElementsByClassName("block");
    for (let i = 0; i < blockElements.length; i++)
        manager.blocks.push(new Block(blockElements[i]));

    manager.bind();

    let editorElement = document.getElementById("editor");
    let blocksElement = document.getElementById("blocks");
    editorElement.style.left = blocksElement.getBoundingClientRect().right + 20;

};
