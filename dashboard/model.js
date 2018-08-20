class Workflow {
	constructor(steps,nodestypes) {
		this.steps = steps;
		this.nodestypes = nodestypes;
	}

	getStepByNodeId(nodeId) {
		for (var i = 0; i < steps.length; i++) {
			if (steps[i].id == nodeId){
				return steps[i];
			}
		}
	}

	addStep(step) {
		this.steps.push(step)
	}

	deleteStep(nodeId) {
		var step = this.getStepByNodeId(nodeId);
		var index = this.steps.indexOf(step);
		if (index > -1) {
          this.steps.splice(index, 1);
      	}
		
	}

	draw() {
		console.log('draw');
	}

	validate() {
		console.log('validate');
	}
}

class NodeType {
	constructor(name,icon,spect) {
		this.name = name;
		this.icon = icon;
		this.spect = spect;
	}
	validate() {
		console.log('validate');
	}
}

class Step {
	constructor(nodeType,id) {
		this.nodeType = nodeType;
		this.id = id;
	}
}

class Multiple extends Step {
	
	addOption(option) {
		if (!this.options){
			this.options = [];
		}
		this.options.push(option);
	}
	deleteOption(option) {
		var index = this.options.indexOf(step);
		if (index > -1) {
          this.options.splice(index, 1);
      	}
	}
}

class Option {
	constructor(text) {
		this.text = text;
	}
	deleteNext() {
		this.next = null;
	}
	addNext(step) {
		this.next = step;
	}
	canAddNext() {
		return !this.next;
	}
}

class Simple extends Step {
	deleteChildStep() {
		this.next = null;
	}
	canAddChildStep() {
		return !this.next;
	}
	addChildStep(step) {
		this.next = step;
	}
}