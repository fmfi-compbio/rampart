
import React from 'react';
import Container, {Title} from "./styles";

class MutationsTree extends React.Component {
    constructor(props) {
        super(props);
        this.state = {};
    }

    createVariantString(variants, level){
        let newText="";
        for(const variant of variants){
            newText+='---'.repeat(level)+"variant: "+ variant.name+" (" + variant.mutations.map(mutation=>mutation.from+mutation.position+mutation.to).join(", ")+")\n";
            if(variant.subs.length>0){
                newText+=this.createVariantString(variant.subs, level+1);
            }
        }
        return newText;
    }


    componentDidMount() {
        let newText=this.createVariantString(this.props.data, 0);
        let newLinesToPtagText = newText.split('\n').map(i => {
            return <p>{i}</p>
        });
        this.setState({data:newLinesToPtagText});      
    }

    componentDidUpdate(prevProps) {
        this.render();
    }


    render() {
        return (
            <Container width="90%" ref="">
                <Title>
                    {"Mutations tree"}
                </Title>
                {this.state.data}
                {this.props.renderProp ? this.props.renderProp : null}
            </Container>
        )
    }
}

export default MutationsTree;