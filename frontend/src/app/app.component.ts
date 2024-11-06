import { Component, OnInit } from '@angular/core';
import { DatasetsService } from './services/datasets.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule} from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatInputModule,
    MatSelectModule,
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',

})
export class AppComponent implements OnInit {
  title = 'frontend';
  datasets: string[] = [];
  datasetsData: any = {};
  queryResult: string = '';

  constructor(
    private _datasetsService: DatasetsService
  ) {}

ngOnInit(): void {
    this._datasetsService.getDatasets().subscribe((data: any) => {
      this.datasets = data.datasets;
    });
  }

getDataset(filename: string): void {
    this._datasetsService.getDatasetFile(filename).subscribe((data: any) => {
      this.datasetsData[filename] = data;
    });
  }

sendQuery(filename: string, question: string): void {
this._datasetsService.sendQuery(filename, question).subscribe(
  (response) => {
    this.queryResult = response.response;
  },
  (error) => console.error('Error querying OpenAI', error)
);
}
}


