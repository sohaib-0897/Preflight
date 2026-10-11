import React from 'react';
import {expect,test,vi} from 'vitest';
import {render,screen,fireEvent,waitFor} from '@testing-library/react';
import {Form,Evidence,Badge} from './ui';
import {percent} from './api';
test('missing metrics remain unknown and evidence text cannot execute markup',()=>{expect(percent(null)).toBe('Unavailable');expect(percent(0)).toBe('0.0%');render(<Evidence value={{output:'<script>alert(1)</script>'}}/>);expect(document.querySelector('script')).toBeNull();expect(screen.getByLabelText('Execution evidence').tabIndex).toBe(0);});
test('invalid account input never calls the server',async()=>{const submit=vi.fn();render(<Form spec={{title:'Create account',fields:[{name:'password',label:'Password',type:'password'}],submit}} onDone={()=>{}}/>);fireEvent.change(screen.getByLabelText('Password'),{target:{value:'short'}});fireEvent.submit(screen.getByRole('button',{name:'Create account'}).closest('form')!);await waitFor(()=>expect(screen.getByRole('alert').textContent).toContain('12'));expect(submit).not.toHaveBeenCalled();});
test('successful async form calls its completion handler',async()=>{const submit=vi.fn().mockResolvedValue(undefined),done=vi.fn();render(<Form spec={{title:'Save',fields:[{name:'name',label:'Name'}],submit}} onDone={done}/>);fireEvent.change(screen.getByLabelText('Name'),{target:{value:'Release evidence'}});fireEvent.submit(screen.getByRole('button',{name:'Save'}).closest('form')!);await waitFor(()=>expect(done).toHaveBeenCalledOnce());expect(submit).toHaveBeenCalledWith({name:'Release evidence'});});
test('unexecuted checks are visibly distinct from passes',()=>{render(<Badge value="NOT_RUN"/>);expect(screen.getByText('NOT RUN').className).not.toContain('good');});
